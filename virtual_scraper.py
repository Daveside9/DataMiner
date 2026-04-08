#!/usr/bin/env python3
"""
Virtual Sports Scraper
Watches Bet9ja Zoom, SportyBet Virtual, Msport Virtual in real-time
and collects every result into the database.

Uses Playwright (headless browser) to handle JavaScript-rendered pages.
"""

import asyncio
import json
import re
import sqlite3
import time
import logging
from datetime import datetime
from pathlib import Path

log = logging.getLogger("VirtualScraper")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

DB_PATH = "virtual_results.db"

# ─── Supported sites config ───────────────────────────────────────────────────
SITES = {
    "bet9ja_zoom": {
        "name":    "Bet9ja Zoom Soccer",
        "url":     "https://web.bet9ja.com/Sport/VirtualSports",
        "type":    "bet9ja",
    },
    "sportybet_virtual": {
        "name":    "SportyBet Virtual Football",
        "url":     "https://www.sportybet.com/ng/virtual-sports/football",
        "type":    "sportybet",
    },
    "msport_virtual": {
        "name":    "Msport Virtual Football",
        "url":     "https://www.msport.com/ng/virtual-sports",
        "type":    "msport",
    },
    "1xbet_virtual": {
        "name":    "1xBet Virtual Football",
        "url":     "https://1xbet.com/en/virtual-sports/football",
        "type":    "1xbet",
    },
}

# ─── Database ─────────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS virtual_results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            site        TEXT NOT NULL,
            game_id     TEXT,
            home_team   TEXT NOT NULL,
            away_team   TEXT NOT NULL,
            home_score  INTEGER NOT NULL,
            away_score  INTEGER NOT NULL,
            result      TEXT NOT NULL,
            total_goals INTEGER NOT NULL,
            both_scored INTEGER NOT NULL,
            scraped_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS scraper_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            site       TEXT,
            status     TEXT,
            message    TEXT,
            logged_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def save_result(site, home, away, hs, as_, game_id=None):
    """Save a scraped result to DB, skip duplicates"""
    result = "home_win" if hs > as_ else "away_win" if as_ > hs else "draw"
    both   = 1 if hs > 0 and as_ > 0 else 0
    total  = hs + as_

    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()

    # Avoid saving exact duplicate in last 2 minutes
    c.execute("""
        SELECT id FROM virtual_results
        WHERE site=? AND home_team=? AND away_team=? AND home_score=? AND away_score=?
        AND scraped_at >= datetime('now', '-2 minutes')
    """, (site, home, away, hs, as_))
    if c.fetchone():
        conn.close()
        return False

    c.execute("""
        INSERT INTO virtual_results
        (site, game_id, home_team, away_team, home_score, away_score, result, total_goals, both_scored)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (site, game_id, home, away, hs, as_, result, total, both))
    conn.commit()
    conn.close()
    log.info(f"[{site}] Saved: {home} {hs}-{as_} {away}")
    return True

def log_scraper(site, status, message):
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()
    c.execute("INSERT INTO scraper_log (site,status,message) VALUES (?,?,?)", (site, status, message))
    conn.commit()
    conn.close()

# ─── Score parser ─────────────────────────────────────────────────────────────

def parse_score(text):
    """Extract home/away score from any text like '2 - 1', '2:1', '2–1'"""
    text = text.strip().replace("–", "-").replace("—", "-")
    m = re.search(r"(\d+)\s*[-:]\s*(\d+)", text)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None

# ─── Scrapers per site ────────────────────────────────────────────────────────

async def scrape_bet9ja(page, site_key):
    """Scrape Bet9ja Zoom Soccer results"""
    try:
        await page.goto(SITES[site_key]["url"], wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(4000)

        # Try multiple selector strategies
        selectors = [
            ".virtual-result",
            ".zoom-result",
            "[class*='result']",
            "[class*='score']",
            ".match-result",
            "table tr",
        ]

        results_found = 0
        for sel in selectors:
            try:
                elements = await page.query_selector_all(sel)
                if not elements:
                    continue

                for el in elements[:20]:
                    text = await el.inner_text()
                    lines = [l.strip() for l in text.split("\n") if l.strip()]

                    # Look for score pattern in text
                    full_text = " ".join(lines)
                    hs, as_ = parse_score(full_text)
                    if hs is None:
                        continue

                    # Try to extract team names
                    teams = re.split(r"\d+\s*[-:]\s*\d+", full_text)
                    home = teams[0].strip() if len(teams) > 0 else "Home Team"
                    away = teams[1].strip() if len(teams) > 1 else "Away Team"

                    # Clean team names
                    home = re.sub(r"[^\w\s]", "", home).strip()[:30]
                    away = re.sub(r"[^\w\s]", "", away).strip()[:30]

                    if home and away and len(home) > 1 and len(away) > 1:
                        saved = save_result(site_key, home, away, hs, as_)
                        if saved:
                            results_found += 1

                if results_found > 0:
                    break
            except Exception:
                continue

        # Fallback: scan all text on page for score patterns
        if results_found == 0:
            body_text = await page.inner_text("body")
            results_found = await _extract_from_body(body_text, site_key)

        log_scraper(site_key, "ok", f"Found {results_found} new results")
        return results_found

    except Exception as e:
        log.warning(f"[{site_key}] Scrape error: {e}")
        log_scraper(site_key, "error", str(e))
        return 0

async def scrape_sportybet(page, site_key):
    """Scrape SportyBet Virtual Football results"""
    try:
        await page.goto(SITES[site_key]["url"], wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(5000)

        selectors = [
            ".virtual-match",
            ".match-item",
            "[class*='virtual']",
            "[class*='match']",
            ".result-item",
        ]

        results_found = 0
        for sel in selectors:
            try:
                elements = await page.query_selector_all(sel)
                for el in elements[:20]:
                    text = await el.inner_text()
                    hs, as_ = parse_score(text)
                    if hs is None:
                        continue
                    teams = re.split(r"\d+\s*[-:]\s*\d+", text)
                    home = teams[0].strip()[:30] if teams else "Home"
                    away = teams[1].strip()[:30] if len(teams) > 1 else "Away"
                    home = re.sub(r"[^\w\s]", "", home).strip()
                    away = re.sub(r"[^\w\s]", "", away).strip()
                    if home and away:
                        saved = save_result(site_key, home, away, hs, as_)
                        if saved:
                            results_found += 1
                if results_found > 0:
                    break
            except Exception:
                continue

        if results_found == 0:
            body_text = await page.inner_text("body")
            results_found = await _extract_from_body(body_text, site_key)

        log_scraper(site_key, "ok", f"Found {results_found} new results")
        return results_found

    except Exception as e:
        log.warning(f"[{site_key}] Scrape error: {e}")
        log_scraper(site_key, "error", str(e))
        return 0

async def scrape_generic(page, site_key):
    """Generic scraper for msport, 1xbet and others"""
    try:
        await page.goto(SITES[site_key]["url"], wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(5000)
        body_text = await page.inner_text("body")
        results_found = await _extract_from_body(body_text, site_key)
        log_scraper(site_key, "ok", f"Found {results_found} new results")
        return results_found
    except Exception as e:
        log.warning(f"[{site_key}] Scrape error: {e}")
        log_scraper(site_key, "error", str(e))
        return 0

async def _extract_from_body(body_text, site_key):
    """
    Last-resort: scan entire page text for score patterns.
    Looks for lines like: 'Arsenal 2 - 1 Chelsea'
    """
    lines = body_text.split("\n")
    results_found = 0

    # Pattern: TeamName Score - Score TeamName
    pattern = re.compile(
        r"([A-Za-z][A-Za-z\s\.]{2,25}?)\s+(\d+)\s*[-:]\s*(\d+)\s+([A-Za-z][A-Za-z\s\.]{2,25})"
    )

    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = pattern.search(line)
        if m:
            home = m.group(1).strip()[:30]
            hs   = int(m.group(2))
            as_  = int(m.group(3))
            away = m.group(4).strip()[:30]

            # Sanity check: scores shouldn't be crazy high for virtual
            if hs > 9 or as_ > 9:
                continue
            if len(home) < 2 or len(away) < 2:
                continue

            saved = save_result(site_key, home, away, hs, as_)
            if saved:
                results_found += 1

    return results_found

# ─── Main scraper loop ────────────────────────────────────────────────────────

SCRAPER_MAP = {
    "bet9ja":   scrape_bet9ja,
    "sportybet": scrape_sportybet,
    "msport":   scrape_generic,
    "1xbet":    scrape_generic,
}

# Global state for the API to read
scraper_status = {k: {"running": False, "last_run": None, "total_collected": 0} for k in SITES}

async def run_scraper(site_key, headless=True, interval=60):
    """
    Continuously scrape a site every `interval` seconds.
    Keeps the browser open between runs to avoid re-loading.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        log.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
        return

    site_type = SITES[site_key]["type"]
    scrape_fn = SCRAPER_MAP.get(site_type, scrape_generic)

    log.info(f"Starting scraper for {SITES[site_key]['name']}")
    scraper_status[site_key]["running"] = True

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()

        # Block images/fonts to speed up loading
        await page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,ttf}", lambda r: r.abort())

        try:
            while scraper_status[site_key]["running"]:
                count = await scrape_fn(page, site_key)
                scraper_status[site_key]["last_run"]       = datetime.now().isoformat()
                scraper_status[site_key]["total_collected"] += count
                await asyncio.sleep(interval)
        finally:
            await browser.close()
            scraper_status[site_key]["running"] = False

def start_scraper_thread(site_key, headless=True, interval=60):
    """Start scraper in a background thread with its own event loop"""
    import threading

    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_scraper(site_key, headless, interval))

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t

def stop_scraper(site_key):
    scraper_status[site_key]["running"] = False

# ─── Manual one-shot scrape (for testing) ────────────────────────────────────

async def scrape_once(site_key, headless=True):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        log.error("Run: pip install playwright && playwright install chromium")
        return []

    site_type = SITES[site_key]["type"]
    scrape_fn = SCRAPER_MAP.get(site_type, scrape_generic)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless, args=["--no-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", lambda r: r.abort())
        count = await scrape_fn(page, site_key)
        await browser.close()
        return count

if __name__ == "__main__":
    init_db()
    print("Testing one-shot scrape of Bet9ja Zoom...")
    result = asyncio.run(scrape_once("bet9ja_zoom", headless=False))
    print(f"Collected {result} results")
