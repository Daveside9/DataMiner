#!/usr/bin/env python3
"""
Pattern Predictor - Advanced analysis for betting patterns like Goal Goal, Over/Under, etc.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
from typing import Dict, List, Any, Tuple
import statistics
import numpy as np

class PatternPredictor:
    def __init__(self, db_path="pattern_analysis.db"):
        self.db_path = db_path
        self.init_database()
        
        # Define betting patterns
        self.patterns = {
            "goal_goal": {
                "name": "Both Teams to Score (Goal Goal)",
                "description": "Both teams score at least 1 goal",
                "check_function": self._check_goal_goal
            },
            "no_goal_goal": {
                "name": "No Goal Goal",
                "description": "At least one team doesn't score",
                "check_function": self._check_no_goal_goal
            },
            "over_2_5": {
                "name": "Over 2.5 Goals",
                "description": "Total goals > 2.5",
                "check_function": self._check_over_2_5
            },
            "under_2_5": {
                "name": "Under 2.5 Goals", 
                "description": "Total goals < 2.5",
                "check_function": self._check_under_2_5
            },
            "over_1_5": {
                "name": "Over 1.5 Goals",
                "description": "Total goals > 1.5",
                "check_function": self._check_over_1_5
            },
            "clean_sheet": {
                "name": "Clean Sheet",
                "description": "One team keeps clean sheet",
                "check_function": self._check_clean_sheet
            },
            "high_scoring": {
                "name": "High Scoring (4+ Goals)",
                "description": "Total goals >= 4",
                "check_function": self._check_high_scoring
            }
        }
    
    def init_database(self):
        """Initialize pattern analysis database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team1 TEXT NOT NULL,
                team2 TEXT NOT NULL,
                score TEXT NOT NULL,
                date TEXT NOT NULL,
                home_goals INTEGER,
                away_goals INTEGER,
                total_goals INTEGER,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                match_date TEXT NOT NULL,
                pattern_result BOOLEAN NOT NULL,
                streak_length INTEGER DEFAULT 1,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                prediction_confidence REAL,
                next_expected_date TEXT,
                reasoning TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_match_data(self, team1: str, team2: str, score: str, date: str, source: str = "manual"):
        """Add match data and extract goals"""
        home_goals, away_goals = self._parse_score(score)
        total_goals = home_goals + away_goals
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO match_data 
            (team1, team2, score, date, home_goals, away_goals, total_goals, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (team1, team2, score, date, home_goals, away_goals, total_goals, source))
        
        match_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Analyze patterns for both teams
        self._analyze_match_patterns(match_id, team1, team2, home_goals, away_goals, date)
        
        return match_id
    
    def _parse_score(self, score: str) -> Tuple[int, int]:
        """Parse score string to extract goals"""
        # Handle various score formats: "2-1", "2:1", "2 - 1", etc.
        score_clean = re.sub(r'[^\d-:]', '', score)
        
        if '-' in score_clean:
            parts = score_clean.split('-')
        elif ':' in score_clean:
            parts = score_clean.split(':')
        else:
            return 0, 0
        
        try:
            home_goals = int(parts[0])
            away_goals = int(parts[1])
            return home_goals, away_goals
        except (ValueError, IndexError):
            return 0, 0
    
    def _analyze_match_patterns(self, match_id: int, team1: str, team2: str, 
                               home_goals: int, away_goals: int, date: str):
        """Analyze patterns for a specific match"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analyze patterns for both teams
        for team in [team1, team2]:
            for pattern_type, pattern_info in self.patterns.items():
                result = pattern_info["check_function"](home_goals, away_goals, team == team1)
                
                # Get current streak
                streak = self._calculate_streak(team, pattern_type, result)
                
                cursor.execute('''
                    INSERT INTO pattern_analysis 
                    (team, pattern_type, match_date, pattern_result, streak_length)
                    VALUES (?, ?, ?, ?, ?)
                ''', (team, pattern_type, date, result, streak))
        
        conn.commit()
        conn.close()
    
    def _calculate_streak(self, team: str, pattern_type: str, current_result: bool) -> int:
        """Calculate current streak for a team's pattern"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern_result FROM pattern_analysis 
            WHERE team = ? AND pattern_type = ?
            ORDER BY match_date DESC
            LIMIT 10
        ''', (team, pattern_type))
        
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not results:
            return 1
        
        # Calculate streak
        streak = 1
        for result in results:
            if result == current_result:
                streak += 1
            else:
                break
        
        return streak
    
    # Pattern checking functions
    def _check_goal_goal(self, home_goals: int, away_goals: int, is_home: bool) -> bool:
        """Both teams score"""
        return home_goals > 0 and away_goals > 0
    
    def _check_no_goal_goal(self, home_goals: int, away_goals: int, is_home: bool) -> bool:
        """At least one team doesn't score"""
        return home_goals == 0 or away_goals == 0
    
    def _check_over_2_5(self, home_goals: int, away_goals: int, is_home: bool) -> bool:
        """Total goals over 2.5"""
        return (home_goals + away_goals) > 2.5
    
    def _check_under_2_5(self, home_goals: int, away_goals: int, is_home: bool) -> bool:
        """Total goals under 2.5"""
        return (home_goals + away_goals) < 2.5
    
    def _check_over_1_5(self, home_goals: int, away_goals: int, is_home: bool) -> bool:
        """Total goals over 1.5"""
        return (home_goals + away_goals) > 1.5
    
    def _check_clean_sheet(self, home_goals: int, away_goals: int, is_home: bool) -> bool:
        """Team keeps clean sheet"""
        if is_home:
            return away_goals == 0
        else:
            return home_goals == 0
    
    def _check_high_scoring(self, home_goals: int, away_goals: int, is_home: bool) -> bool:
        """High scoring match (4+ goals)"""
        return (home_goals + away_goals) >= 4
    
    def analyze_team_patterns(self, team: str, days_back: int = 30) -> Dict[str, Any]:
        """Comprehensive pattern analysis for a team"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent matches
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT pattern_type, pattern_result, match_date, streak_length
            FROM pattern_analysis 
            WHERE team = ? AND match_date >= ?
            ORDER BY match_date DESC
        ''', (team, cutoff_date))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {"error": f"No data found for {team} in the last {days_back} days"}
        
        # Organize data by pattern
        pattern_data = defaultdict(list)
        for pattern_type, result, date, streak in results:
            pattern_data[pattern_type].append({
                'result': bool(result),
                'date': date,
                'streak': streak
            })
        
        analysis = {
            "team": team,
            "analysis_period": f"Last {days_back} days",
            "total_matches": len(set(r[2] for r in results)) // len(self.patterns),
            "patterns": {}
        }
        
        # Analyze each pattern
        for pattern_type, pattern_info in self.patterns.items():
            if pattern_type in pattern_data:
                pattern_analysis = self._analyze_single_pattern(
                    team, pattern_type, pattern_data[pattern_type], pattern_info
                )
                analysis["patterns"][pattern_type] = pattern_analysis
        
        return analysis
    
    def _analyze_single_pattern(self, team: str, pattern_type: str, 
                               data: List[Dict], pattern_info: Dict) -> Dict[str, Any]:
        """Analyze a single pattern for detailed insights"""
        if not data:
            return {"error": "No data available"}
        
        # Basic statistics
        total_matches = len(data)
        successful_matches = sum(1 for d in data if d['result'])
        success_rate = (successful_matches / total_matches) * 100
        
        # Current streak
        current_streak = data[0]['streak'] if data else 0
        current_streak_type = "winning" if data[0]['result'] else "losing"
        
        # Streak analysis
        streaks = [d['streak'] for d in data]
        max_streak = max(streaks) if streaks else 0
        avg_streak = statistics.mean(streaks) if streaks else 0
        
        # Pattern frequency analysis
        recent_results = [d['result'] for d in data[:10]]  # Last 10 matches
        recent_success_rate = (sum(recent_results) / len(recent_results)) * 100 if recent_results else 0
        
        # Trend analysis
        trend = self._calculate_trend(data)
        
        # Prediction
        prediction = self._predict_next_occurrence(team, pattern_type, data)
        
        return {
            "name": pattern_info["name"],
            "description": pattern_info["description"],
            "statistics": {
                "total_matches": total_matches,
                "successful_matches": successful_matches,
                "success_rate": round(success_rate, 2),
                "recent_success_rate": round(recent_success_rate, 2)
            },
            "streaks": {
                "current_streak": current_streak,
                "current_streak_type": current_streak_type,
                "max_streak": max_streak,
                "average_streak": round(avg_streak, 2)
            },
            "trend": trend,
            "prediction": prediction,
            "recent_matches": data[:5]  # Last 5 matches
        }
    
    def _calculate_trend(self, data: List[Dict]) -> str:
        """Calculate if pattern is trending up, down, or stable"""
        if len(data) < 4:
            return "insufficient_data"
        
        # Compare first half vs second half
        mid_point = len(data) // 2
        first_half = data[mid_point:]
        second_half = data[:mid_point]
        
        first_success_rate = sum(1 for d in first_half if d['result']) / len(first_half)
        second_success_rate = sum(1 for d in second_half if d['result']) / len(second_half)
        
        difference = second_success_rate - first_success_rate
        
        if difference > 0.2:
            return "trending_up"
        elif difference < -0.2:
            return "trending_down"
        else:
            return "stable"
    
    def _predict_next_occurrence(self, team: str, pattern_type: str, data: List[Dict]) -> Dict[str, Any]:
        """Predict when pattern might occur next"""
        if len(data) < 3:
            return {"confidence": 0, "reasoning": "Insufficient data for prediction"}
        
        # Calculate various factors
        success_rate = sum(1 for d in data if d['result']) / len(data)
        recent_success_rate = sum(1 for d in data[:5] if d['result']) / min(5, len(data))
        current_streak = data[0]['streak']
        is_current_winning = data[0]['result']
        
        # Simple prediction logic
        confidence = 0
        reasoning = []
        
        # Base confidence on success rate
        confidence += success_rate * 50
        
        # Adjust for recent form
        if recent_success_rate > success_rate:
            confidence += 20
            reasoning.append("Recent form is better than average")
        elif recent_success_rate < success_rate:
            confidence -= 15
            reasoning.append("Recent form is below average")
        
        # Adjust for current streak
        if is_current_winning and current_streak >= 3:
            confidence += 15
            reasoning.append(f"Currently on a {current_streak}-match winning streak")
        elif not is_current_winning and current_streak >= 3:
            confidence -= 10
            reasoning.append(f"Currently on a {current_streak}-match losing streak")
        
        # Pattern-specific adjustments
        if pattern_type == "goal_goal":
            if success_rate > 0.6:
                confidence += 10
                reasoning.append("Team has strong Goal Goal record")
        
        # Cap confidence
        confidence = max(0, min(100, confidence))
        
        return {
            "confidence": round(confidence, 1),
            "next_match_probability": f"{confidence:.1f}%",
            "reasoning": reasoning,
            "recommendation": self._get_recommendation(confidence, pattern_type)
        }
    
    def _get_recommendation(self, confidence: float, pattern_type: str) -> str:
        """Get betting recommendation based on confidence"""
        if confidence >= 75:
            return f"Strong bet on {pattern_type}"
        elif confidence >= 60:
            return f"Consider betting on {pattern_type}"
        elif confidence >= 40:
            return f"Neutral - monitor {pattern_type}"
        else:
            return f"Avoid betting on {pattern_type}"
    
    def get_pattern_insights(self, team: str, pattern_type: str = "goal_goal") -> Dict[str, Any]:
        """Get detailed insights for a specific pattern"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all historical data for this pattern
        cursor.execute('''
            SELECT pattern_result, match_date, streak_length
            FROM pattern_analysis 
            WHERE team = ? AND pattern_type = ?
            ORDER BY match_date DESC
        ''', (team, pattern_type))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {"error": f"No {pattern_type} data found for {team}"}
        
        # Detailed analysis
        total_matches = len(results)
        successful = sum(1 for r in results if r[0])
        success_rate = (successful / total_matches) * 100
        
        # Find patterns in the data
        pattern_sequence = [bool(r[0]) for r in results]
        
        # Analyze streaks
        streaks = self._analyze_streaks(pattern_sequence)
        
        # Monthly breakdown
        monthly_stats = self._get_monthly_breakdown(results)
        
        # When does pattern break/start
        pattern_changes = self._analyze_pattern_changes(results)
        
        return {
            "team": team,
            "pattern": pattern_type,
            "overall_stats": {
                "total_matches": total_matches,
                "successful": successful,
                "success_rate": round(success_rate, 2)
            },
            "streak_analysis": streaks,
            "monthly_breakdown": monthly_stats,
            "pattern_changes": pattern_changes,
            "next_prediction": self._predict_next_occurrence(team, pattern_type, 
                [{"result": bool(r[0]), "date": r[1], "streak": r[2]} for r in results[:10]])
        }
    
    def _analyze_streaks(self, sequence: List[bool]) -> Dict[str, Any]:
        """Analyze winning and losing streaks"""
        if not sequence:
            return {}
        
        streaks = []
        current_streak = 1
        current_type = sequence[0]
        
        for i in range(1, len(sequence)):
            if sequence[i] == current_type:
                current_streak += 1
            else:
                streaks.append({"type": current_type, "length": current_streak})
                current_streak = 1
                current_type = sequence[i]
        
        # Add final streak
        streaks.append({"type": current_type, "length": current_streak})
        
        # Analyze streaks
        winning_streaks = [s["length"] for s in streaks if s["type"]]
        losing_streaks = [s["length"] for s in streaks if not s["type"]]
        
        return {
            "longest_winning_streak": max(winning_streaks) if winning_streaks else 0,
            "longest_losing_streak": max(losing_streaks) if losing_streaks else 0,
            "average_winning_streak": round(statistics.mean(winning_streaks), 2) if winning_streaks else 0,
            "average_losing_streak": round(statistics.mean(losing_streaks), 2) if losing_streaks else 0,
            "total_winning_streaks": len(winning_streaks),
            "total_losing_streaks": len(losing_streaks)
        }
    
    def _get_monthly_breakdown(self, results: List[Tuple]) -> Dict[str, Any]:
        """Break down pattern success by month"""
        monthly_data = defaultdict(lambda: {"total": 0, "successful": 0})
        
        for result, date, _ in results:
            try:
                month = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m')
                monthly_data[month]["total"] += 1
                if result:
                    monthly_data[month]["successful"] += 1
            except ValueError:
                continue
        
        # Calculate success rates
        monthly_stats = {}
        for month, data in monthly_data.items():
            success_rate = (data["successful"] / data["total"]) * 100 if data["total"] > 0 else 0
            monthly_stats[month] = {
                "total_matches": data["total"],
                "successful": data["successful"],
                "success_rate": round(success_rate, 2)
            }
        
        return monthly_stats
    
    def _analyze_pattern_changes(self, results: List[Tuple]) -> Dict[str, Any]:
        """Analyze when patterns change and why"""
        changes = []
        
        for i in range(1, len(results)):
            current = bool(results[i-1][0])
            previous = bool(results[i][0])
            
            if current != previous:
                changes.append({
                    "date": results[i-1][1],
                    "change_type": "started" if current else "ended",
                    "previous_streak": results[i][2]
                })
        
        # Analyze change patterns
        starts = [c for c in changes if c["change_type"] == "started"]
        ends = [c for c in changes if c["change_type"] == "ended"]
        
        return {
            "total_changes": len(changes),
            "pattern_starts": len(starts),
            "pattern_ends": len(ends),
            "average_streak_before_change": round(statistics.mean([c["previous_streak"] for c in changes]), 2) if changes else 0,
            "recent_changes": changes[:5]  # Last 5 changes
        }

def main():
    """Demo the pattern predictor"""
    predictor = PatternPredictor()
    
    print("🎯 Pattern Predictor Demo")
    print("=" * 50)
    
    # Add some sample data
    sample_matches = [
        ("Real Madrid", "Barcelona", "2-1", "2024-01-01"),
        ("Real Madrid", "Atletico", "3-2", "2024-01-05"),
        ("Real Madrid", "Valencia", "1-0", "2024-01-10"),
        ("Real Madrid", "Sevilla", "2-2", "2024-01-15"),
        ("Real Madrid", "Villarreal", "4-1", "2024-01-20"),
    ]
    
    for team1, team2, score, date in sample_matches:
        predictor.add_match_data(team1, team2, score, date)
    
    # Analyze patterns
    analysis = predictor.analyze_team_patterns("Real Madrid", 30)
    
    print(f"\n📊 PATTERN ANALYSIS FOR {analysis['team']}")
    print(f"Period: {analysis['analysis_period']}")
    print(f"Total matches: {analysis['total_matches']}")
    
    for pattern_type, pattern_data in analysis["patterns"].items():
        print(f"\n🎲 {pattern_data['name']}")
        print(f"   Success rate: {pattern_data['statistics']['success_rate']}%")
        print(f"   Current streak: {pattern_data['streaks']['current_streak']} ({pattern_data['streaks']['current_streak_type']})")
        print(f"   Prediction: {pattern_data['prediction']['next_match_probability']} confidence")
        print(f"   Recommendation: {pattern_data['prediction']['recommendation']}")
    
    # Detailed Goal Goal analysis
    print(f"\n🥅 DETAILED GOAL GOAL ANALYSIS")
    goal_goal_insights = predictor.get_pattern_insights("Real Madrid", "goal_goal")
    
    if "error" not in goal_goal_insights:
        print(f"Overall success rate: {goal_goal_insights['overall_stats']['success_rate']}%")
        print(f"Longest winning streak: {goal_goal_insights['streak_analysis']['longest_winning_streak']}")
        print(f"Longest losing streak: {goal_goal_insights['streak_analysis']['longest_losing_streak']}")

if __name__ == "__main__":
    main()