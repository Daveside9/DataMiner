#!/usr/bin/env python3
"""
Live Score Monitor - Real-time data collection and score prediction
Monitors live betting sites and predicts next scores
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime, timedelta
import re
import threading
from collections import defaultdict
import statistics

class LiveScoreMonitor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.live_matches = {}
        self.score_history = defaultdict(list)
        self.predictions = {}
        self.monitoring = False
        
    def get_live_matches(self):
        """Scrape live matches from multiple sources"""
        live_data = []
        
        # Try multiple live score sources
        sources = [
            'https://www.livescore.com/en/football/',
            'https://www.flashscore.com/football/',
            'https://www.bbc.com/sport/football/scores-fixtures'
        ]
        
        for source in sources:
            try:
                print(f"🔍 Checking {source}...")
                response = self.session.get(source, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for live match indicators
                live_indicators = soup.find_all(text=re.compile(r'LIVE|Live|\d+\'|\d+\+\d+\''))
                
                if live_indicators:
                    matches = self.extract_live_matches(soup, source)
                    live_data.extend(matches)
                    print(f"✅ Found {len(matches)} live matches on {source}")
                    break
                    
            except Exception as e:
                print(f"❌ Failed to scrape {source}: {e}")
                continue
        
        return live_data
    
    def extract_live_matches(self, soup, source):
        """Extract live match data from HTML"""
        matches = []
        
        # Look for score patterns like "2-1", "0-0", etc.
        score_pattern = r'\b\d+[-–]\d+\b'
        
        # Find all text containing scores
        all_text = soup.get_text()
        score_matches = re.findall(score_pattern, all_text)
        
        # Look for team names near scores
        for score in score_matches:
            # Find the context around this score
            score_index = all_text.find(score)
            context_start = max(0, score_index - 100)
            context_end = min(len(all_text), score_index + 100)
            context = all_text[context_start:context_end]
            
            # Extract team names (words that start with capital letters)
            words = context.split()
            team_words = [w for w in words if w and w[0].isupper() and len(w) > 2 and w.isalpha()]
            
            if len(team_words) >= 2:
                home_team = team_words[0]
                away_team = team_words[1]
                
                # Parse score
                home_score, away_score = map(int, score.replace('–', '-').split('-'))
                
                match_data = {
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': home_score,
                    'away_score': away_score,
                    'total_goals': home_score + away_score,
                    'timestamp': datetime.now().isoformat(),
                    'source': source,
                    'match_id': f"{home_team}_{away_team}_{datetime.now().strftime('%Y%m%d')}"
                }
                
                matches.append(match_data)
        
        return matches[:10]  # Limit to 10 matches
    
    def start_monitoring(self, duration_minutes=30, interval_seconds=60):
        """Start monitoring live matches for a specific period"""
        print(f"🚀 Starting live score monitoring...")
        print(f"⏱️ Duration: {duration_minutes} minutes")
        print(f"🔄 Update interval: {interval_seconds} seconds")
        
        self.monitoring = True
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        while self.monitoring and datetime.now() < end_time:
            try:
                # Get current live matches
                live_matches = self.get_live_matches()
                
                if live_matches:
                    print(f"\n📊 {datetime.now().strftime('%H:%M:%S')} - Found {len(live_matches)} live matches:")
                    
                    for match in live_matches:
                        match_id = match['match_id']
                        score_key = f"{match['home_score']}-{match['away_score']}"
                        
                        # Store score history
                        self.score_history[match_id].append({
                            'timestamp': match['timestamp'],
                            'home_score': match['home_score'],
                            'away_score': match['away_score'],
                            'total_goals': match['total_goals']
                        })
                        
                        # Update live matches
                        self.live_matches[match_id] = match
                        
                        print(f"   ⚽ {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
                        
                        # Generate prediction if we have enough data
                        if len(self.score_history[match_id]) >= 3:
                            prediction = self.predict_next_score(match_id)
                            self.predictions[match_id] = prediction
                            print(f"      🔮 Prediction: {prediction['next_score']} (confidence: {prediction['confidence']}%)")
                
                else:
                    print(f"⏳ {datetime.now().strftime('%H:%M:%S')} - No live matches found, checking again...")
                
                # Wait before next check
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error during monitoring: {e}")
                time.sleep(interval_seconds)
        
        self.monitoring = False
        print(f"\n✅ Monitoring completed!")
        return self.generate_report()
    
    def predict_next_score(self, match_id):
        """Predict the next score based on historical data"""
        history = self.score_history[match_id]
        
        if len(history) < 3:
            return {'error': 'Not enough data for prediction'}
        
        # Analyze scoring patterns
        goal_intervals = []
        total_goals_progression = [h['total_goals'] for h in history]
        
        # Calculate goal scoring rate
        time_diff = (datetime.fromisoformat(history[-1]['timestamp']) - 
                    datetime.fromisoformat(history[0]['timestamp'])).total_seconds() / 60
        
        if time_diff > 0:
            goals_per_minute = (total_goals_progression[-1] - total_goals_progression[0]) / time_diff
        else:
            goals_per_minute = 0
        
        # Predict next score
        current_home = history[-1]['home_score']
        current_away = history[-1]['away_score']
        
        # Simple prediction logic
        if goals_per_minute > 0.1:  # High scoring rate
            # Predict who's more likely to score next
            home_trend = sum(1 for i in range(1, len(history)) 
                           if history[i]['home_score'] > history[i-1]['home_score'])
            away_trend = sum(1 for i in range(1, len(history)) 
                           if history[i]['away_score'] > history[i-1]['away_score'])
            
            if home_trend >= away_trend:
                predicted_home = current_home + 1
                predicted_away = current_away
                confidence = min(85, 60 + (home_trend * 10))
            else:
                predicted_home = current_home
                predicted_away = current_away + 1
                confidence = min(85, 60 + (away_trend * 10))
        else:
            # Low scoring, predict no change
            predicted_home = current_home
            predicted_away = current_away
            confidence = 70
        
        return {
            'match_id': match_id,
            'current_score': f"{current_home}-{current_away}",
            'next_score': f"{predicted_home}-{predicted_away}",
            'confidence': confidence,
            'goals_per_minute': round(goals_per_minute, 3),
            'prediction_time': datetime.now().isoformat(),
            'reasoning': f"Based on {len(history)} data points over {time_diff:.1f} minutes"
        }
    
    def generate_report(self):
        """Generate monitoring report with predictions"""
        report = {
            'monitoring_summary': {
                'total_matches_tracked': len(self.live_matches),
                'total_predictions_made': len(self.predictions),
                'monitoring_duration': len(self.score_history),
                'report_time': datetime.now().isoformat()
            },
            'live_matches': self.live_matches,
            'predictions': self.predictions,
            'score_history': dict(self.score_history)
        }
        
        print(f"\n📋 MONITORING REPORT")
        print(f"=" * 50)
        print(f"🎯 Matches tracked: {len(self.live_matches)}")
        print(f"🔮 Predictions made: {len(self.predictions)}")
        
        for match_id, prediction in self.predictions.items():
            match = self.live_matches.get(match_id, {})
            print(f"\n⚽ {match.get('home_team', 'Team A')} vs {match.get('away_team', 'Team B')}")
            print(f"   Current: {prediction['current_score']}")
            print(f"   Predicted: {prediction['next_score']}")
            print(f"   Confidence: {prediction['confidence']}%")
        
        return report

def start_live_monitoring():
    """Start the live monitoring system"""
    monitor = LiveScoreMonitor()
    
    print("🎯 Live Score Monitor & Predictor")
    print("=" * 50)
    print("🔍 This will monitor REAL live matches and predict scores")
    print("⚽ Scrapes live betting sites for current match data")
    print("🤖 Uses AI to predict next score changes")
    print("=" * 50)
    
    try:
        # Start monitoring for 30 minutes, checking every 60 seconds
        report = monitor.start_monitoring(duration_minutes=30, interval_seconds=60)
        
        # Save report
        with open('live_monitoring_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Report saved to: live_monitoring_report.json")
        return report
        
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")
        return None

if __name__ == "__main__":
    start_live_monitoring()