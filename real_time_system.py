#!/usr/bin/env python3
"""
Real-Time Sports Monitoring System
Combines live scraping, screen monitoring, and AI prediction
"""

import json
import time
from datetime import datetime, timedelta
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

class RealTimeSportsSystem:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.live_matches = {}
        self.predictions = {}
        self.monitoring_active = False
        self.setup_routes()
        
    def setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/api/start-monitoring', methods=['POST'])
        def start_monitoring():
            data = request.get_json()
            target_url = data.get('url', 'https://www.livescore.com/en/football/')
            duration = data.get('duration', 15)  # minutes
            interval = data.get('interval', 60)   # seconds
            specific_teams = data.get('specific_teams', [])  # List of teams to monitor
            
            if self.monitoring_active:
                return jsonify({'error': 'Monitoring already active'}), 400
            
            # Start monitoring in background thread
            thread = threading.Thread(
                target=self.start_live_monitoring,
                args=(target_url, duration, interval, specific_teams)
            )
            thread.daemon = True
            thread.start()
            
            teams_msg = f" for teams: {', '.join(specific_teams)}" if specific_teams else " for all teams"
            
            return jsonify({
                'success': True,
                'message': f'Started monitoring {target_url} for {duration} minutes{teams_msg}',
                'monitoring_id': int(time.time())
            })
        
        @self.app.route('/api/stop-monitoring', methods=['POST'])
        def stop_monitoring():
            self.monitoring_active = False
            return jsonify({'success': True, 'message': 'Monitoring stopped'})
        
        @self.app.route('/api/live-matches', methods=['GET'])
        def get_live_matches():
            return jsonify({
                'matches': self.live_matches,
                'predictions': self.predictions,
                'monitoring_active': self.monitoring_active,
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/predict-score', methods=['POST'])
        def predict_score():
            data = request.get_json()
            match_id = data.get('match_id')
            
            if match_id in self.live_matches:
                prediction = self.generate_prediction(match_id)
                self.predictions[match_id] = prediction
                return jsonify({'success': True, 'prediction': prediction})
            else:
                return jsonify({'error': 'Match not found'}), 404
    
    def start_live_monitoring(self, url, duration_minutes, interval_seconds, specific_teams=None):
        """Start live monitoring process with optional team filtering"""
        print(f"🚀 Starting real-time monitoring...")
        print(f"🌐 URL: {url}")
        print(f"⏱️ Duration: {duration_minutes} minutes")
        print(f"🔄 Interval: {interval_seconds} seconds")
        if specific_teams:
            print(f"🎯 Monitoring specific teams: {', '.join(specific_teams)}")
        else:
            print(f"🎯 Monitoring all teams")
        
        self.monitoring_active = True
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        while self.monitoring_active and datetime.now() < end_time:
            try:
                # Scrape live data
                live_data = self.scrape_live_scores(url, specific_teams)
                
                if live_data:
                    print(f"📊 {datetime.now().strftime('%H:%M:%S')} - Found {len(live_data)} live matches")
                    
                    for match in live_data:
                        match_id = match['match_id']
                        
                        # Update match history
                        if match_id not in self.live_matches:
                            self.live_matches[match_id] = {
                                'home_team': match['home_team'],
                                'away_team': match['away_team'],
                                'history': []
                            }
                        
                        self.live_matches[match_id]['history'].append({
                            'timestamp': match['timestamp'],
                            'home_score': match['home_score'],
                            'away_score': match['away_score'],
                            'total_goals': match['total_goals']
                        })
                        
                        print(f"   ⚽ {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']} (REAL DATA)")
                        
                        # Generate prediction if enough data
                        if len(self.live_matches[match_id]['history']) >= 3:
                            prediction = self.generate_prediction(match_id)
                            self.predictions[match_id] = prediction
                            print(f"      🔮 Next: {prediction['predicted_score']} ({prediction['confidence']}%)")
                
                else:
                    print(f"⏳ {datetime.now().strftime('%H:%M:%S')} - No live matches found")
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(interval_seconds)
        
        self.monitoring_active = False
        print("✅ Monitoring completed!")
    
    def scrape_live_scores(self, url, specific_teams=None):
        """Scrape live scores using enhanced scraper with Bet9ja support"""
        try:
            # Check if it's a Bet9ja URL
            if 'bet9ja.com' in url:
                print("🇳🇬 Using Bet9ja specialized scraper...")
                try:
                    from bet9ja_scraper import Bet9jaScraper
                    bet9ja_scraper = Bet9jaScraper()
                    matches = bet9ja_scraper.scrape_bet9ja_live(specific_teams)
                    
                    if matches:
                        print(f"🎉 Bet9ja scraper found {len(matches)} matches!")
                        return matches
                    else:
                        print("❌ Bet9ja scraper found no matches")
                        return []
                except ImportError:
                    print("⚠️ Bet9ja scraper not available, using enhanced scraper...")
                except Exception as e:
                    print(f"❌ Bet9ja scraper error: {e}, falling back to enhanced scraper...")
            
            # Use enhanced scraper for other sites
            from enhanced_scraper import EnhancedScraper
            
            scraper = EnhancedScraper()
            matches = scraper.scrape_live_scores(url, specific_teams)
            
            if matches:
                print(f"🎉 Enhanced scraper found {len(matches)} REAL matches!")
                return matches
            else:
                print("❌ Enhanced scraper found no matches - website may not have live games right now")
                return []
                
        except ImportError:
            print("⚠️ Enhanced scraper not available, using basic method...")
            return self.scrape_live_scores_basic(url, specific_teams)
        except Exception as e:
            print(f"❌ Enhanced scraping failed: {e}")
            return self.scrape_live_scores_basic(url, specific_teams)
    
    def scrape_live_scores_basic(self, url, specific_teams=None):
        """Basic scraping fallback method"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            print(f"🔍 Basic scraping from: {url}")
            if specific_teams:
                print(f"🎯 Looking for teams: {', '.join(specific_teams)}")
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code} - Website may be blocking requests")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            page_text = soup.get_text()
            
            print(f"📄 Page loaded: {len(page_text)} characters")
            
            matches = []
            
            # AGGRESSIVE PATTERN MATCHING - Find ANY score-like patterns
            score_patterns = [
                r'\b\d+\s*[-–—]\s*\d+\b',      # 2-1, 2 - 1, 2–1
                r'\b\d+\s*:\s*\d+\b',          # 2:1
                r'\(\s*\d+\s*[-–]\s*\d+\s*\)', # (2-1)
                r'\d+\s*/\s*\d+',              # 2/1
                r'\b\d+\s+\d+\b',              # 2 1 (space separated)
            ]
            
            all_scores = []
            for pattern in score_patterns:
                scores = re.findall(pattern, page_text, re.IGNORECASE)
                for score in scores:
                    # Clean and validate score
                    clean_score = re.sub(r'[^\d\-–—:/\s]', '', score).strip()
                    if clean_score and len(clean_score) >= 3:
                        all_scores.append(clean_score)
            
            # Remove duplicates and filter valid scores
            unique_scores = []
            seen = set()
            for score in all_scores:
                normalized = re.sub(r'[^\d]', '-', score)
                if normalized not in seen:
                    try:
                        # Try to parse as score
                        parts = re.split(r'[-–—:/\s]+', normalized)
                        if len(parts) == 2:
                            home_val = int(parts[0])
                            away_val = int(parts[1])
                            # Valid football scores (0-20 range)
                            if 0 <= home_val <= 20 and 0 <= away_val <= 20:
                                unique_scores.append((home_val, away_val, score))
                                seen.add(normalized)
                    except (ValueError, IndexError):
                        continue
            
            print(f"🎯 Found {len(unique_scores)} valid scores: {[s[2] for s in unique_scores[:5]]}")
            
            # ENHANCED TEAM DETECTION
            # Look for team names in various formats
            team_patterns = [
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:FC|CF|AC|SC|United|City|Town|Rovers|Wanderers|Athletic|Hotspur))\b',
                r'\b(?:Arsenal|Chelsea|Liverpool|Manchester\s+(?:City|United)|Tottenham|Barcelona|Real\s+Madrid|Bayern|PSG|Juventus|Milan|Inter)\b',
                r'\b[A-Z]{3,4}\b',  # 3-4 letter abbreviations
                r'\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b'  # Two word teams
            ]
            
            all_teams = []
            for pattern in team_patterns:
                teams = re.findall(pattern, page_text, re.IGNORECASE)
                all_teams.extend(teams)
            
            # Filter and clean team names
            excluded_words = {
                'Live', 'Score', 'Match', 'Game', 'Today', 'Tomorrow', 'Yesterday', 
                'Premier', 'League', 'Championship', 'Division', 'Table', 'News',
                'Home', 'Away', 'Full', 'Time', 'Half', 'Final', 'Result', 'Goals',
                'Cards', 'Corners', 'Fouls', 'Shots', 'Possession', 'Substitutions',
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December',
                'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
            }
            
            filtered_teams = []
            for team in all_teams:
                team_clean = team.strip()
                if (team_clean not in excluded_words and 
                    len(team_clean) > 2 and 
                    not team_clean.isdigit() and
                    team_clean not in filtered_teams):
                    filtered_teams.append(team_clean)
            
            print(f"⚽ Found {len(filtered_teams)} potential teams: {filtered_teams[:10]}")
            
            # MATCH SCORES WITH TEAMS
            for i, (home_score, away_score, original_score) in enumerate(unique_scores[:10]):
                # Try to find teams near this score in the text
                score_index = page_text.find(original_score)
                if score_index != -1:
                    # Look for team names around the score
                    context_start = max(0, score_index - 200)
                    context_end = min(len(page_text), score_index + 200)
                    context = page_text[context_start:context_end]
                    
                    # Find teams in context
                    context_teams = []
                    for team in filtered_teams:
                        if team.lower() in context.lower():
                            context_teams.append(team)
                    
                    # Assign teams
                    if len(context_teams) >= 2:
                        home_team = context_teams[0]
                        away_team = context_teams[1]
                    elif len(context_teams) == 1:
                        home_team = context_teams[0]
                        away_team = filtered_teams[min(i + 1, len(filtered_teams) - 1)] if filtered_teams else f"Team{i+1}B"
                    else:
                        # Use positional teams
                        if i * 2 + 1 < len(filtered_teams):
                            home_team = filtered_teams[i * 2]
                            away_team = filtered_teams[i * 2 + 1]
                        else:
                            continue  # Skip if no teams available
                
                else:
                    # Fallback team assignment
                    if i * 2 + 1 < len(filtered_teams):
                        home_team = filtered_teams[i * 2]
                        away_team = filtered_teams[i * 2 + 1]
                    else:
                        continue
                
                # Apply team filter if specified
                if specific_teams:
                    team_match = False
                    for target_team in specific_teams:
                        if (target_team.lower() in home_team.lower() or 
                            target_team.lower() in away_team.lower()):
                            team_match = True
                            break
                    
                    if not team_match:
                        continue  # Skip this match if teams don't match filter
                
                match_data = {
                    'match_id': f"{home_team.replace(' ', '_')}_{away_team.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': home_score,
                    'away_score': away_score,
                    'total_goals': home_score + away_score,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'BASIC_SCRAPING',
                    'url': url,
                    'original_score': original_score
                }
                
                matches.append(match_data)
                print(f"✅ Match: {home_team} {home_score}-{away_score} {away_team} (from: {original_score})")
            
            if matches:
                print(f"🎉 Basic scraping found {len(matches)} matches!")
                return matches
            else:
                print("❌ No valid matches found - website may not have live games right now")
                return []
                
        except Exception as e:
            print(f"❌ Basic scraping failed: {e}")
            return []
    
    def generate_prediction(self, match_id):
        """Generate AI prediction for next score"""
        match = self.live_matches[match_id]
        history = match['history']
        
        if len(history) < 3:
            return {'error': 'Insufficient data'}
        
        # Analyze recent scoring patterns
        recent = history[-3:]
        current = recent[-1]
        
        # Calculate scoring trends
        goal_changes = []
        for i in range(1, len(recent)):
            prev_goals = recent[i-1]['total_goals']
            curr_goals = recent[i]['total_goals']
            goal_changes.append(curr_goals - prev_goals)
        
        avg_goal_change = sum(goal_changes) / len(goal_changes) if goal_changes else 0
        
        # Current scores
        current_home = current['home_score']
        current_away = current['away_score']
        
        # Prediction logic
        if avg_goal_change > 0.5:
            # High scoring rate
            if current_home >= current_away:
                predicted_home = current_home + 1
                predicted_away = current_away
                confidence = 75
                reasoning = "Home team scoring trend"
            else:
                predicted_home = current_home
                predicted_away = current_away + 1
                confidence = 75
                reasoning = "Away team scoring trend"
        elif avg_goal_change > 0:
            # Moderate scoring
            predicted_home = current_home + 1
            predicted_away = current_away
            confidence = 60
            reasoning = "Moderate scoring pattern"
        else:
            # Low scoring
            predicted_home = current_home
            predicted_away = current_away
            confidence = 80
            reasoning = "Low scoring match"
        
        return {
            'match_id': match_id,
            'current_score': f"{current_home}-{current_away}",
            'predicted_score': f"{predicted_home}-{predicted_away}",
            'confidence': confidence,
            'reasoning': reasoning,
            'avg_goal_change': round(avg_goal_change, 2),
            'data_points': len(history),
            'prediction_time': datetime.now().isoformat()
        }
    
    def run_server(self, host='localhost', port=5001):
        """Run the Flask server"""
        print(f"🚀 Real-Time Sports System starting...")
        print(f"📡 API Server: http://{host}:{port}")
        print(f"🌐 Frontend: http://localhost:3000/live-score-predictor.html")
        print(f"🤖 AI Prediction Engine: Ready")
        print("=" * 60)
        
        self.app.run(host=host, port=port, debug=False)

def main():
    """Main function to start the real-time system"""
    system = RealTimeSportsSystem()
    
    print("🎯 Real-Time Sports Monitoring & Prediction System")
    print("=" * 60)
    print("✅ Features:")
    print("   📡 Live score scraping from betting sites")
    print("   🤖 AI-powered score prediction")
    print("   📊 Real-time data analysis")
    print("   🔮 Next goal/score predictions")
    print("   📈 Pattern recognition")
    print("=" * 60)
    
    try:
        system.run_server()
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")

if __name__ == "__main__":
    main()