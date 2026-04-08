#!/usr/bin/env python3
"""
Virtual Sports AI Predictor
Reads ALL collected results from the DB and predicts the next game output
using frequency analysis, streak detection, and pattern scoring.

Since virtual sports are RNG-based, this uses statistical inference:
- Score frequency distribution
- Home/Away/Draw ratio
- Over/Under 2.5 streaks
- Both Teams to Score (BTTS) patterns
- Hot/Cold score detection
- Markov chain transition probabilities
"""

import sqlite3
import json
import math
from datetime import datetime
from collections import Counter, defaultdict

DB_PATH = "virtual_results.db"


class VirtualSportsAI:

    def __init__(self, site=None, min_samples=10):
        self.site        = site
        self.min_samples = min_samples

    # ── Data loading ──────────────────────────────────────────────────────────

    def _load(self, site=None, limit=500):
        conn = sqlite3.connect(DB_PATH)
        c    = conn.cursor()
        s    = site or self.site
        if s:
            c.execute("""
                SELECT home_team, away_team, home_score, away_score, result,
                       total_goals, both_scored, scraped_at
                FROM virtual_results WHERE site=?
                ORDER BY id DESC LIMIT ?
            """, (s, limit))
        else:
            c.execute("""
                SELECT home_team, away_team, home_score, away_score, result,
                       total_goals, both_scored, scraped_at
                FROM virtual_results
                ORDER BY id DESC LIMIT ?
            """, (limit,))
        rows = c.fetchall()
        conn.close()
        return rows  # newest first

    # ── Core analysis ─────────────────────────────────────────────────────────

    def analyze(self, site=None):
        rows = self._load(site)
        if len(rows) < self.min_samples:
            return {
                "error": f"Not enough data yet. Need {self.min_samples} results, have {len(rows)}. Keep the scraper running.",
                "collected": len(rows),
                "needed": self.min_samples,
            }

        scores      = [(r[2], r[3]) for r in rows]          # (home, away)
        results     = [r[4] for r in rows]                   # home_win/away_win/draw
        totals      = [r[5] for r in rows]                   # total goals
        btts        = [bool(r[6]) for r in rows]             # both scored

        n = len(rows)

        # ── 1. Result distribution ────────────────────────────────────────────
        result_counts = Counter(results)
        home_win_pct  = result_counts["home_win"] / n * 100
        away_win_pct  = result_counts["away_win"] / n * 100
        draw_pct      = result_counts["draw"]     / n * 100

        # ── 2. Score frequency ────────────────────────────────────────────────
        score_counts  = Counter(scores)
        top_scores    = score_counts.most_common(10)

        # ── 3. Over/Under ─────────────────────────────────────────────────────
        over25_pct    = sum(1 for t in totals if t > 2) / n * 100
        over15_pct    = sum(1 for t in totals if t > 1) / n * 100
        avg_goals     = sum(totals) / n

        # ── 4. BTTS ───────────────────────────────────────────────────────────
        btts_pct      = sum(btts) / n * 100

        # ── 5. Current streaks (most recent games) ────────────────────────────
        streaks = self._calc_streaks(results, totals, btts)

        # ── 6. Markov transition (last result → next result probability) ──────
        markov = self._markov(results)

        # ── 7. Hot scores (appeared more than expected) ───────────────────────
        expected_per_score = n / 100  # ~100 possible scores 0-0 to 9-9
        hot_scores = [
            {"score": f"{h}-{a}", "count": cnt, "pct": round(cnt / n * 100, 1)}
            for (h, a), cnt in top_scores[:5]
        ]

        # ── 8. Next game prediction ───────────────────────────────────────────
        prediction = self._predict_next(
            results, scores, totals, btts,
            home_win_pct, away_win_pct, draw_pct,
            over25_pct, btts_pct, streaks, markov, top_scores
        )

        return {
            "site":          site or self.site or "all",
            "total_analyzed": n,
            "result_distribution": {
                "home_win": round(home_win_pct, 1),
                "away_win": round(away_win_pct, 1),
                "draw":     round(draw_pct,     1),
            },
            "goals": {
                "average":    round(avg_goals, 2),
                "over_1_5":   round(over15_pct, 1),
                "over_2_5":   round(over25_pct, 1),
                "btts":       round(btts_pct,   1),
            },
            "hot_scores":    hot_scores,
            "streaks":       streaks,
            "markov":        markov,
            "prediction":    prediction,
            "timestamp":     datetime.now().isoformat(),
        }

    # ── Streak calculator ─────────────────────────────────────────────────────

    def _calc_streaks(self, results, totals, btts):
        def streak(seq, match_fn):
            count = 0
            for v in seq:          # newest first
                if match_fn(v):
                    count += 1
                else:
                    break
            return count

        return {
            "current_result":      results[0] if results else None,
            "result_streak":       streak(results, lambda v: v == results[0]),
            "over25_streak":       streak(totals,  lambda v: v > 2),
            "under25_streak":      streak(totals,  lambda v: v <= 2),
            "btts_streak":         streak(btts,    lambda v: v is True),
            "no_btts_streak":      streak(btts,    lambda v: v is False),
            "last_5_results":      results[:5],
            "last_5_totals":       totals[:5],
        }

    # ── Markov chain ──────────────────────────────────────────────────────────

    def _markov(self, results):
        transitions = defaultdict(Counter)
        for i in range(len(results) - 1):
            current = results[i + 1]   # previous game (older)
            next_   = results[i]       # next game (newer)
            transitions[current][next_] += 1

        matrix = {}
        for state, nexts in transitions.items():
            total = sum(nexts.values())
            matrix[state] = {k: round(v / total * 100, 1) for k, v in nexts.items()}

        return matrix

    # ── Main prediction engine ────────────────────────────────────────────────

    def _predict_next(self, results, scores, totals, btts,
                      hw_pct, aw_pct, draw_pct,
                      over25_pct, btts_pct, streaks, markov, top_scores):

        suggestions = []
        confidence_factors = []

        # ── A. Result prediction ──────────────────────────────────────────────
        last_result = results[0] if results else None
        result_streak = streaks["result_streak"]

        # Use Markov if we have transitions
        if last_result and last_result in markov:
            trans = markov[last_result]
            predicted_result = max(trans, key=trans.get)
            result_conf = trans[predicted_result]
        else:
            # Fall back to frequency
            predicted_result = max(
                [("home_win", hw_pct), ("away_win", aw_pct), ("draw", draw_pct)],
                key=lambda x: x[1]
            )[0]
            result_conf = max(hw_pct, aw_pct, draw_pct)

        # Streak reversal logic: if same result 4+ times, lean toward change
        if result_streak >= 4:
            others = [r for r in ["home_win", "away_win", "draw"] if r != last_result]
            # pick the most frequent of the others
            other_counts = Counter(r for r in results if r != last_result)
            if other_counts:
                predicted_result = other_counts.most_common(1)[0][0]
                result_conf = min(result_conf + 10, 85)
                suggestions.append(f"Streak reversal likely after {result_streak} consecutive {last_result.replace('_',' ')}s")

        confidence_factors.append(result_conf)

        # ── B. Score prediction ───────────────────────────────────────────────
        # Weight top scores by frequency, bias toward predicted result
        result_filter = {
            "home_win": lambda h, a: h > a,
            "away_win": lambda h, a: a > h,
            "draw":     lambda h, a: h == a,
        }
        fn = result_filter.get(predicted_result, lambda h, a: True)

        filtered = [(s, cnt) for s, cnt in top_scores if fn(s[0], s[1])]
        if not filtered:
            filtered = top_scores  # fallback

        best_score = filtered[0][0]
        score_conf = filtered[0][1] / len(scores) * 100

        # ── C. Over/Under prediction ──────────────────────────────────────────
        over25_streak  = streaks["over25_streak"]
        under25_streak = streaks["under25_streak"]

        if over25_streak >= 3:
            over_under = "Under 2.5"
            ou_conf    = 60 + over25_streak * 3
            suggestions.append(f"Over 2.5 on {over25_streak}-game streak — Under likely next")
        elif under25_streak >= 3:
            over_under = "Over 2.5"
            ou_conf    = 60 + under25_streak * 3
            suggestions.append(f"Under 2.5 on {under25_streak}-game streak — Over likely next")
        elif over25_pct > 60:
            over_under = "Over 2.5"
            ou_conf    = over25_pct
        else:
            over_under = "Under 2.5"
            ou_conf    = 100 - over25_pct

        # ── D. BTTS prediction ────────────────────────────────────────────────
        btts_streak    = streaks["btts_streak"]
        no_btts_streak = streaks["no_btts_streak"]

        if btts_streak >= 4:
            btts_pred = "No BTTS"
            btts_conf = 65
            suggestions.append(f"BTTS on {btts_streak}-game streak — No BTTS likely")
        elif no_btts_streak >= 4:
            btts_pred = "BTTS"
            btts_conf = 65
            suggestions.append(f"No BTTS on {no_btts_streak}-game streak — BTTS likely")
        elif btts_pct > 55:
            btts_pred = "BTTS"
            btts_conf = btts_pct
        else:
            btts_pred = "No BTTS"
            btts_conf = 100 - btts_pct

        # ── E. Overall confidence ─────────────────────────────────────────────
        overall_conf = round(
            (result_conf * 0.4 + ou_conf * 0.3 + btts_conf * 0.3), 1
        )
        overall_conf = min(overall_conf, 82)  # cap — we're honest about RNG

        label_map = {"home_win": "Home Win", "away_win": "Away Win", "draw": "Draw"}

        return {
            "predicted_result":  label_map.get(predicted_result, predicted_result),
            "predicted_score":   f"{best_score[0]}-{best_score[1]}",
            "over_under":        over_under,
            "btts":              btts_pred,
            "confidence":        overall_conf,
            "result_confidence": round(result_conf, 1),
            "ou_confidence":     round(min(ou_conf, 85), 1),
            "btts_confidence":   round(min(btts_conf, 85), 1),
            "suggestions":       suggestions,
            "disclaimer":        "Virtual sports use RNG. These are statistical patterns, not guarantees.",
        }

    # ── Per-team stats (if teams are consistent across games) ─────────────────

    def team_stats(self, team, site=None):
        conn = sqlite3.connect(DB_PATH)
        c    = conn.cursor()
        s    = site or self.site
        if s:
            c.execute("""
                SELECT home_team, away_team, home_score, away_score
                FROM virtual_results
                WHERE site=? AND (home_team LIKE ? OR away_team LIKE ?)
                ORDER BY id DESC LIMIT 100
            """, (s, f"%{team}%", f"%{team}%"))
        else:
            c.execute("""
                SELECT home_team, away_team, home_score, away_score
                FROM virtual_results
                WHERE home_team LIKE ? OR away_team LIKE ?
                ORDER BY id DESC LIMIT 100
            """, (f"%{team}%", f"%{team}%"))
        rows = c.fetchall()
        conn.close()

        if not rows:
            return {"error": f"No data for team: {team}"}

        played = wins = draws = losses = gf = gc = 0
        for home, away, hs, as_ in rows:
            is_home = team.lower() in home.lower()
            scored    = hs if is_home else as_
            conceded  = as_ if is_home else hs
            gf += scored; gc += conceded; played += 1
            if scored > conceded:   wins   += 1
            elif scored == conceded: draws  += 1
            else:                    losses += 1

        return {
            "team":    team,
            "played":  played,
            "wins":    wins,
            "draws":   draws,
            "losses":  losses,
            "goals_for":     gf,
            "goals_against": gc,
            "avg_scored":    round(gf / played, 2),
            "avg_conceded":  round(gc / played, 2),
            "win_rate":      round(wins / played * 100, 1),
        }

    # ── Recent results list ───────────────────────────────────────────────────

    def recent_results(self, site=None, limit=30):
        rows = self._load(site, limit=limit)
        return [
            {
                "home_team":  r[0],
                "away_team":  r[1],
                "home_score": r[2],
                "away_score": r[3],
                "result":     r[4],
                "total_goals": r[5],
                "btts":       bool(r[6]),
                "scraped_at": r[7],
            }
            for r in rows
        ]

    # ── DB stats ──────────────────────────────────────────────────────────────

    def db_stats(self):
        conn = sqlite3.connect(DB_PATH)
        c    = conn.cursor()
        c.execute("SELECT COUNT(*) FROM virtual_results")
        total = c.fetchone()[0]
        c.execute("SELECT site, COUNT(*) FROM virtual_results GROUP BY site")
        by_site = dict(c.fetchall())
        c.execute("SELECT COUNT(*) FROM virtual_results WHERE scraped_at >= datetime('now','-1 hour')")
        last_hour = c.fetchone()[0]
        conn.close()
        return {"total": total, "by_site": by_site, "last_hour": last_hour}


if __name__ == "__main__":
    from virtual_scraper import init_db
    init_db()

    ai = VirtualSportsAI()
    stats = ai.db_stats()
    print(f"Total results in DB: {stats['total']}")

    result = ai.analyze()
    if "error" in result:
        print(result["error"])
    else:
        p = result["prediction"]
        print(f"\nPrediction:")
        print(f"  Result:     {p['predicted_result']} ({p['result_confidence']}%)")
        print(f"  Score:      {p['predicted_score']}")
        print(f"  Over/Under: {p['over_under']} ({p['ou_confidence']}%)")
        print(f"  BTTS:       {p['btts']} ({p['btts_confidence']}%)")
        print(f"  Confidence: {p['confidence']}%")
