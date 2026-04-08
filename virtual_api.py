#!/usr/bin/env python3
"""
Virtual Sports Prediction API
Flask backend that ties the scraper + AI together.
Run this, then open the React frontend.
"""

import json
import threading
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

from virtual_scraper import (
    init_db, SITES, scraper_status,
    start_scraper_thread, stop_scraper,
)
from virtual_ai import VirtualSportsAI

app  = Flask(__name__)
CORS(app)
ai   = VirtualSportsAI()

init_db()

# ─── Scraper control ──────────────────────────────────────────────────────────

@app.route("/api/virt/sites", methods=["GET"])
def get_sites():
    sites = []
    for key, info in SITES.items():
        sites.append({
            "id":      key,
            "name":    info["name"],
            "url":     info["url"],
            "running": scraper_status[key]["running"],
            "last_run": scraper_status[key]["last_run"],
            "collected": scraper_status[key]["total_collected"],
        })
    return jsonify({"sites": sites})

@app.route("/api/virt/start", methods=["POST"])
def start_scraper():
    body     = request.get_json() or {}
    site_key = body.get("site")
    headless = body.get("headless", True)
    interval = int(body.get("interval", 60))

    if site_key not in SITES:
        return jsonify({"error": f"Unknown site: {site_key}"}), 400

    if scraper_status[site_key]["running"]:
        return jsonify({"message": f"Scraper for {site_key} already running"})

    start_scraper_thread(site_key, headless=headless, interval=interval)
    return jsonify({"message": f"Scraper started for {SITES[site_key]['name']}", "site": site_key})

@app.route("/api/virt/stop", methods=["POST"])
def stop_scraper_route():
    body     = request.get_json() or {}
    site_key = body.get("site")
    if site_key not in SITES:
        return jsonify({"error": "Unknown site"}), 400
    stop_scraper(site_key)
    return jsonify({"message": f"Scraper stopped for {site_key}"})

@app.route("/api/virt/status", methods=["GET"])
def scraper_status_route():
    return jsonify({"status": scraper_status})

# ─── Manual data entry (user types in results they see) ──────────────────────

@app.route("/api/virt/add-result", methods=["POST"])
def add_result():
    """
    User can manually enter results they see on the betting site.
    This is the most reliable way to collect data.
    """
    from virtual_scraper import save_result
    body = request.get_json() or {}

    site  = body.get("site", "manual")
    home  = body.get("home_team", "").strip()
    away  = body.get("away_team", "").strip()
    hs    = body.get("home_score")
    as_   = body.get("away_score")

    if not home or not away or hs is None or as_ is None:
        return jsonify({"error": "home_team, away_team, home_score, away_score required"}), 400

    try:
        hs  = int(hs)
        as_ = int(as_)
    except ValueError:
        return jsonify({"error": "Scores must be integers"}), 400

    saved = save_result(site, home, away, hs, as_)
    return jsonify({"saved": saved, "message": "Result added" if saved else "Duplicate skipped"})

@app.route("/api/virt/bulk-add", methods=["POST"])
def bulk_add():
    """Add multiple results at once"""
    from virtual_scraper import save_result
    body    = request.get_json() or {}
    site    = body.get("site", "manual")
    results = body.get("results", [])

    saved_count = 0
    for r in results:
        try:
            ok = save_result(
                site,
                r["home_team"], r["away_team"],
                int(r["home_score"]), int(r["away_score"])
            )
            if ok:
                saved_count += 1
        except Exception:
            continue

    return jsonify({"saved": saved_count, "total": len(results)})

# ─── AI Prediction ────────────────────────────────────────────────────────────

@app.route("/api/virt/predict", methods=["GET"])
def predict():
    site = request.args.get("site")
    result = ai.analyze(site)
    return jsonify(result)

@app.route("/api/virt/team-stats", methods=["GET"])
def team_stats():
    team = request.args.get("team", "")
    site = request.args.get("site")
    if not team:
        return jsonify({"error": "team parameter required"}), 400
    return jsonify(ai.team_stats(team, site))

# ─── Results data ─────────────────────────────────────────────────────────────

@app.route("/api/virt/results", methods=["GET"])
def get_results():
    site  = request.args.get("site")
    limit = int(request.args.get("limit", 50))
    return jsonify({"results": ai.recent_results(site, limit)})

@app.route("/api/virt/stats", methods=["GET"])
def db_stats():
    return jsonify(ai.db_stats())

@app.route("/api/virt/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  Virtual Sports Prediction API  — port 5055")
    print("=" * 55)
    print("  POST /api/virt/start        start scraper")
    print("  POST /api/virt/stop         stop scraper")
    print("  POST /api/virt/add-result   manual result entry")
    print("  POST /api/virt/bulk-add     bulk result entry")
    print("  GET  /api/virt/predict      AI prediction")
    print("  GET  /api/virt/results      recent results")
    print("  GET  /api/virt/stats        DB stats")
    print("=" * 55)
    app.run(host="0.0.0.0", port=5055, debug=False, threaded=True)
