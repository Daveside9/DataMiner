#!/usr/bin/env python3
"""
Sports Data Mining Bot
Advanced bot for mining historical sports data, monitoring screens, and analyzing patterns
"""

import time
import json
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

class SportsDataMiningBot:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize databases
        self.init_databases()
        
        # Bot status
        self.mining_active = False
        self.screen_monitoring_active = False
        self.historical_data = {}
        self.team_patterns = {}
        self.live_odds = {}
        
        # Setup routes
        self.setup_routes()
        
        print("🤖 Sports Data Mining Bot initialized!")
    
    def init_databases(self):
        """Initialize SQLite databases for storing mined data"""
        os.makedirs('data', exist_ok=True)
        
        # Historical matches database
        self.matches_db = sqlite3.connect('data/sports_matches.db', check_same_thread=False)
        self.matches_db.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_home TEXT,
                team_away TEXT,
                score_home INTEGER,
                score_away INTEGER,
                match_date TEXT,
                league TEXT,
                venue TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Team analysis database
        self.analysis_db = sqlite3.connect('data/team_analysis.db', check_same_thread=False)
        self.analysis_db.execute('''
            CREATE TABLE IF NOT EXISTS team_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT,
                analysis_data TEXT,
                patterns TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("✅ Databases initialized")
    
    def setup_routes(self):
        """Setup Flask API routes"""
        
        # Add CORS support for all routes
        @self.app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        @self.app.route('/api/start-data-mining', methods=['POST', 'OPTIONS'])
        def start_data_mining():
            data = request.get_json()
            teams = data.get('teams', [])
            time_period = data.get('time_period', '3_months')
            sources = data.get('sources', ['flashscore', 'bbc_sport'])
            
            if self.mining_active:
                return jsonify({'error': 'Data mining already active'}), 400
            
            # Start mining in background
            thread = threading.Thread(
                target=self.start_comprehensive_mining,
                args=(teams, time_period, sources)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'message': f'Started mining data for {len(teams)} teams',
                'teams': teams,
                'time_period': time_period
            })
        
        @self.app.route('/api/mine-team-history', methods=['POST'])
        def mine_team_history():
            data = request.get_json()
            team_name = data.get('team_name')
            analysis_period = data.get('analysis_period', '6_months')
            
            if not team_name:
                return jsonify({'error': 'Team name required'}), 400
            
            # Mine team history
            result = self.mine_single_team_history(team_name, analysis_period)
            
            return jsonify({
                'success': True,
                'team': team_name,
                'analysis': result
            })
        
        @self.app.route('/api/predict-score', methods=['POST'])
        def predict_score():
            data = request.get_json()
            home_team = data.get('home_team')
            away_team = data.get('away_team')
            league = data.get('league')
            odds_data = data.get('odds_data')
            historical_data = data.get('historical_data')
            
            if not home_team or not away_team:
                return jsonify({'error': 'Both home_team and away_team required'}), 400
            
            try:
                from score_predictor import ScorePredictor
                
                predictor = ScorePredictor()
                prediction = predictor.predict_match_score(
                    home_team=home_team,
                    away_team=away_team,
                    league=league,
                    odds_data=odds_data,
                    historical_data=historical_data
                )
                
                return jsonify({
                    'success': True,
                    'prediction': prediction
                })
                
            except Exception as e:
                return jsonify({'error': f'Prediction error: {str(e)}'}), 500
        
        @self.app.route('/api/predict-from-bet9ja', methods=['POST'])
        def predict_from_bet9ja():
            data = request.get_json()
            url = data.get('url')
            
            if not url:
                return jsonify({'error': 'Bet9ja URL required'}), 400
            
            try:
                # First extract data from Bet9ja
                from bet9ja_history_extractor import Bet9jaHistoryExtractor
                from score_predictor import ScorePredictor
                
                extractor = Bet9jaHistoryExtractor()
                bet9ja_data = extractor.extract_match_history_from_url(url)
                
                if not bet9ja_data or not isinstance(bet9ja_data, dict):
                    return jsonify({'error': 'Could not extract data from Bet9ja URL'}), 400
                
                # Extract match details
                teams = bet9ja_data.get('teams', {})
                home_team = teams.get('home_team')
                away_team = teams.get('away_team')
                league = teams.get('league')
                odds_data = bet9ja_data.get('current_odds', {})
                historical_data = bet9ja_data.get('historical_matches', [])
                
                if not home_team or not away_team:
                    return jsonify({'error': 'Could not identify teams from Bet9ja data'}), 400
                
                # Generate prediction
                predictor = ScorePredictor()
                prediction = predictor.predict_match_score(
                    home_team=home_team,
                    away_team=away_team,
                    league=league,
                    odds_data=odds_data,
                    historical_data=historical_data,
                    live_score=bet9ja_data.get('live_score'),
                    is_live=bet9ja_data.get('is_live', False)
                )
                
                # Store prediction
                self.store_prediction(prediction, bet9ja_data)
                
                return jsonify({
                    'success': True,
                    'bet9ja_data': bet9ja_data,
                    'prediction': prediction,
                    'message': f'Score prediction generated for {home_team} vs {away_team}'
                })
                
            except Exception as e:
                return jsonify({'error': f'Prediction error: {str(e)}'}), 500
        
        @self.app.route('/api/extract-bet9ja-history', methods=['POST', 'OPTIONS'])
        def extract_bet9ja_history():
            if request.method == 'OPTIONS':
                return '', 200
                
            data = request.get_json()
            url = data.get('url')
            
            if not url:
                return jsonify({'error': 'Bet9ja URL required'}), 400
            
            try:
                from bet9ja_history_extractor import Bet9jaHistoryExtractor
                
                extractor = Bet9jaHistoryExtractor()
                result = extractor.extract_match_history_from_url(url)
                
                if result and isinstance(result, dict):
                    # Store the extracted data
                    self.store_bet9ja_data(result)
                    
                    return jsonify({
                        'success': True,
                        'message': 'Bet9ja history extracted successfully',
                        'data': result,
                        'teams_found': result.get('teams', {}),
                        'odds_count': len(result.get('current_odds', {})),
                        'historical_count': len(result.get('historical_matches', []))
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'No data could be extracted from the Bet9ja URL',
                        'message': 'The page may be loading slowly or the URL format is not supported'
                    }), 400
                    
            except ImportError as e:
                return jsonify({'error': f'Bet9ja extractor not available: {str(e)}'}), 500
            except Exception as e:
                return jsonify({'error': f'Extraction error: {str(e)}'}), 500
        
        @self.app.route('/api/analyze-teams-comprehensive', methods=['POST'])
        def analyze_teams_comprehensive():
            data = request.get_json()
            match_url = data.get('url')
            
            if not match_url:
                return jsonify({'error': 'Match URL required'}), 400
            
            try:
                from advanced_team_analyzer import AdvancedTeamAnalyzer
                
                analyzer = AdvancedTeamAnalyzer()
                analysis = analyzer.analyze_teams_from_url(match_url)
                
                if analysis:
                    # Store the analysis
                    self.store_comprehensive_analysis(analysis)
                    
                    return jsonify({
                        'success': True,
                        'analysis': analysis,
                        'message': f'Comprehensive analysis completed for {analysis["match_info"]["home_team"]} vs {analysis["match_info"]["away_team"]}'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Could not analyze teams from the provided URL'
                    }), 400
                    
            except Exception as e:
                return jsonify({'error': f'Analysis error: {str(e)}'}), 500
        def extract_bet9ja_history():
            data = request.get_json()
            url = data.get('url')
            
            if not url:
                return jsonify({'error': 'Bet9ja URL required'}), 400
            
            try:
                # Import and use Bet9ja extractor
                from bet9ja_history_extractor import Bet9jaHistoryExtractor
                
                extractor = Bet9jaHistoryExtractor()
                result = extractor.extract_match_history_from_url(url)
                
                if result and isinstance(result, dict):
                    # Store the extracted data
                    self.store_bet9ja_data(result)
                    
                    return jsonify({
                        'success': True,
                        'message': 'Bet9ja history extracted successfully',
                        'data': result,
                        'teams_found': result.get('teams', {}),
                        'odds_count': len(result.get('current_odds', {})),
                        'historical_count': len(result.get('historical_matches', []))
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'No data could be extracted from the Bet9ja URL',
                        'message': 'The page may be loading slowly or the URL format is not supported'
                    }), 400
                    
            except ImportError as e:
                return jsonify({'error': f'Bet9ja extractor not available: {str(e)}'}), 500
            except Exception as e:
                return jsonify({'error': f'Extraction error: {str(e)}'}), 500
        
        @self.app.route('/api/start-screen-monitoring', methods=['POST'])
        def start_screen_monitoring():
            data = request.get_json()
            urls = data.get('urls', [])
            interval = data.get('interval', 30)
            
            if self.screen_monitoring_active:
                return jsonify({'error': 'Screen monitoring already active'}), 400
            
            thread = threading.Thread(
                target=self.start_advanced_screen_monitoring,
                args=(urls, interval)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'message': 'Advanced screen monitoring started',
                'monitoring_urls': len(urls)
            })
        
        @self.app.route('/api/get-mined-data', methods=['GET'])
        def get_mined_data():
            team = request.args.get('team')
            
            if team:
                # Get specific team data
                cursor = self.analysis_db.cursor()
                cursor.execute('SELECT * FROM team_stats WHERE team_name = ? ORDER BY last_updated DESC LIMIT 1', (team,))
                result = cursor.fetchone()
                
                if result:
                    return jsonify({
                        'team': team,
                        'analysis': json.loads(result[2]),
                        'patterns': json.loads(result[3]),
                        'last_updated': result[4]
                    })
                else:
                    return jsonify({'error': 'No data found for team'}), 404
            else:
                # Get all teams summary
                cursor = self.analysis_db.cursor()
                cursor.execute('SELECT team_name, last_updated FROM team_stats ORDER BY last_updated DESC')
                teams = cursor.fetchall()
                
                return jsonify({
                    'teams_analyzed': len(teams),
                    'teams': [{'name': t[0], 'last_updated': t[1]} for t in teams]
                })
        
        @self.app.route('/api/bot-status', methods=['GET'])
        def get_bot_status():
            return jsonify({
                'mining_active': self.mining_active,
                'screen_monitoring_active': self.screen_monitoring_active,
                'teams_in_database': self.get_teams_count(),
                'matches_in_database': self.get_matches_count(),
                'last_mining_session': self.get_last_mining_time()
            })
    
    def start_comprehensive_mining(self, teams, time_period, sources):
        """Start comprehensive data mining for multiple teams"""
        print(f"🚀 Starting comprehensive data mining...")
        print(f"📊 Teams: {', '.join(teams)}")
        print(f"⏱️ Period: {time_period}")
        print(f"🌐 Sources: {', '.join(sources)}")
        
        self.mining_active = True
        
        try:
            for team in teams:
                if not self.mining_active:
                    break
                
                print(f"\n🔍 Mining data for {team}...")
                
                # Mine from each source
                for source in sources:
                    try:
                        data = self.mine_from_source(team, source, time_period)
                        if data:
                            self.store_team_data(team, data, source)
                            print(f"✅ {team} data from {source}: {len(data.get('matches', []))} matches")
                    except Exception as e:
                        print(f"❌ Error mining {team} from {source}: {e}")
                
                # Analyze patterns
                analysis = self.analyze_team_patterns(team)
                self.store_team_analysis(team, analysis)
                
                time.sleep(2)  # Rate limiting
            
            print("✅ Comprehensive mining completed!")
            
        except Exception as e:
            print(f"❌ Mining error: {e}")
        finally:
            self.mining_active = False
    
    def mine_single_team_history(self, team_name, analysis_period):
        """Mine comprehensive history for a single team"""
        print(f"🔍 Mining comprehensive history for {team_name}...")
        
        # Use the Arsenal analyzer as a template for other teams
        try:
            from arsenal_analyzer import ArsenalAnalyzer
            
            # Adapt for any team
            analyzer = ArsenalAnalyzer()
            
            # Override team name in analyzer
            analyzer.team_name = team_name
            
            # Get comprehensive report
            report = analyzer.generate_report()
            
            # Store in database
            self.store_team_analysis(team_name, report)
            
            return report
            
        except ImportError:
            # Fallback to basic mining
            return self.mine_team_basic(team_name, analysis_period)
    
    def mine_team_basic(self, team_name, analysis_period):
        """Basic team mining fallback"""
        print(f"📊 Basic mining for {team_name}...")
        
        # Calculate date range
        end_date = datetime.now()
        if analysis_period == '1_month':
            start_date = end_date - timedelta(days=30)
        elif analysis_period == '3_months':
            start_date = end_date - timedelta(days=90)
        elif analysis_period == '6_months':
            start_date = end_date - timedelta(days=180)
        else:
            start_date = end_date - timedelta(days=365)
        
        # Mine from multiple sources
        all_matches = []
        sources = [
            f'https://www.flashscore.com/search/?q={team_name.replace(" ", "+")}',
            f'https://www.bbc.com/sport/football/teams/{team_name.lower().replace(" ", "-")}',
            f'https://www.livescore.com/en/football/team/{team_name.replace(" ", "-").lower()}/'
        ]
        
        for source_url in sources:
            try:
                matches = self.scrape_team_matches(team_name, source_url)
                all_matches.extend(matches)
            except Exception as e:
                print(f"❌ Error scraping {source_url}: {e}")
        
        # Analyze patterns
        analysis = {
            'team_name': team_name,
            'analysis_period': analysis_period,
            'matches_found': len(all_matches),
            'recent_form': self.calculate_recent_form(all_matches),
            'scoring_patterns': self.analyze_scoring_patterns(all_matches),
            'venue_performance': self.analyze_venue_performance(all_matches),
            'opponent_analysis': self.analyze_opponents(all_matches),
            'predictions': self.generate_team_predictions(all_matches),
            'timestamp': datetime.now().isoformat()
        }
        
        return analysis
    
    def scrape_team_matches(self, team_name, url):
        """Scrape matches for a specific team from a URL"""
        matches = []
        
        try:
            # Setup Chrome driver
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            driver.get(url)
            time.sleep(5)
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            text_content = soup.get_text()
            
            # Enhanced pattern matching for team matches
            patterns = [
                rf'{re.escape(team_name)}\s+(\d+)\s*[-–:]\s*(\d+)\s+([A-Z][a-zA-Z\s]+)',
                rf'([A-Z][a-zA-Z\s]+)\s+(\d+)\s*[-–:]\s*(\d+)\s+{re.escape(team_name)}',
                rf'{re.escape(team_name)}\s+vs?\s+([A-Z][a-zA-Z\s]+)\s+(\d+)\s*[-–:]\s*(\d+)',
            ]
            
            for pattern in patterns:
                pattern_matches = re.finditer(pattern, text_content, re.IGNORECASE)
                for match in pattern_matches:
                    try:
                        # Parse match data
                        if team_name.lower() in match.group(0).lower():
                            match_data = self.parse_match_data(match, team_name)
                            if match_data:
                                matches.append(match_data)
                    except Exception as e:
                        continue
            
            driver.quit()
            
        except Exception as e:
            print(f"❌ Scraping error: {e}")
        
        return matches[:20]  # Limit to 20 most recent matches
    
    def parse_match_data(self, match, team_name):
        """Parse individual match data"""
        try:
            groups = match.groups()
            match_text = match.group(0)
            
            # Determine home/away and scores
            if match_text.lower().startswith(team_name.lower()):
                # Team was home
                home_team = team_name
                away_team = groups[-1] if len(groups) >= 3 else groups[0]
                home_score = int(groups[0]) if groups[0].isdigit() else int(groups[1])
                away_score = int(groups[1]) if groups[1].isdigit() else int(groups[2])
            else:
                # Team was away
                home_team = groups[0]
                away_team = team_name
                home_score = int(groups[1])
                away_score = int(groups[2])
            
            return {
                'home_team': home_team.strip(),
                'away_team': away_team.strip(),
                'home_score': home_score,
                'away_score': away_score,
                'match_date': datetime.now() - timedelta(days=len(self.historical_data)),
                'venue': 'Home' if home_team == team_name else 'Away',
                'result': self.determine_result(home_score, away_score, team_name, home_team)
            }
        except Exception as e:
            return None
    
    def determine_result(self, home_score, away_score, team_name, home_team):
        """Determine match result for the team"""
        team_score = home_score if home_team == team_name else away_score
        opponent_score = away_score if home_team == team_name else home_score
        
        if team_score > opponent_score:
            return 'Win'
        elif team_score < opponent_score:
            return 'Loss'
        else:
            return 'Draw'
    
    def start_advanced_screen_monitoring(self, urls, interval):
        """Start advanced screen monitoring with AI analysis"""
        print(f"📸 Starting advanced screen monitoring...")
        print(f"🌐 URLs: {len(urls)}")
        print(f"⏱️ Interval: {interval}s")
        
        self.screen_monitoring_active = True
        
        try:
            while self.screen_monitoring_active:
                for url in urls:
                    if not self.screen_monitoring_active:
                        break
                    
                    try:
                        # Take screenshot and analyze
                        screenshot_data = self.capture_and_analyze_screen(url)
                        
                        if screenshot_data:
                            # Detect changes and extract data
                            changes = self.detect_screen_changes(screenshot_data)
                            odds_data = self.extract_odds_from_screen(screenshot_data)
                            
                            if changes or odds_data:
                                print(f"📊 Screen analysis: {len(changes)} changes, {len(odds_data)} odds detected")
                                
                                # Store data
                                self.store_screen_data(url, screenshot_data, changes, odds_data)
                    
                    except Exception as e:
                        print(f"❌ Screen monitoring error for {url}: {e}")
                
                time.sleep(interval)
        
        except Exception as e:
            print(f"❌ Screen monitoring error: {e}")
        finally:
            self.screen_monitoring_active = False
            print("✅ Screen monitoring stopped")
    
    def capture_and_analyze_screen(self, url):
        """Capture screenshot and perform AI analysis"""
        try:
            # Setup Chrome for high-quality screenshots
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--force-device-scale-factor=1")
            
            driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            driver.get(url)
            time.sleep(8)  # Wait for full load
            
            # Take screenshot
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = f'screenshots/mining_bot_{timestamp}.png'
            
            os.makedirs('screenshots', exist_ok=True)
            driver.save_screenshot(screenshot_path)
            
            # Get page content for text analysis
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            driver.quit()
            
            return {
                'timestamp': timestamp,
                'url': url,
                'screenshot_path': screenshot_path,
                'page_text': page_text[:5000],  # First 5000 chars
                'file_size': os.path.getsize(screenshot_path) if os.path.exists(screenshot_path) else 0
            }
        
        except Exception as e:
            print(f"❌ Screenshot capture error: {e}")
            return None
    
    def detect_screen_changes(self, screenshot_data):
        """Detect changes in screen content using AI"""
        changes = []
        
        try:
            # Simple change detection based on text content
            current_text = screenshot_data['page_text']
            
            # Compare with previous capture (simplified)
            if hasattr(self, 'previous_screen_text'):
                if current_text != self.previous_screen_text:
                    # Calculate change percentage
                    diff_chars = sum(1 for a, b in zip(current_text, self.previous_screen_text) if a != b)
                    change_percentage = (diff_chars / len(current_text)) * 100 if current_text else 0
                    
                    if change_percentage > 1:  # More than 1% change
                        changes.append({
                            'type': 'content_change',
                            'percentage': change_percentage,
                            'description': f'{change_percentage:.1f}% of content changed'
                        })
            
            self.previous_screen_text = current_text
            
        except Exception as e:
            print(f"❌ Change detection error: {e}")
        
        return changes
    
    def extract_odds_from_screen(self, screenshot_data):
        """Extract betting odds from screen content"""
        odds_data = []
        
        try:
            text = screenshot_data['page_text']
            
            # Enhanced odds patterns
            odds_patterns = {
                'decimal': r'\b[1-9]\.\d{2}\b',
                'fractional': r'\b\d+/\d+\b',
                'american_plus': r'\+\d{3,4}\b',
                'american_minus': r'-\d{3,4}\b',
                'over_under': r'Over\s+\d+\.?\d*|Under\s+\d+\.?\d*'
            }
            
            for odds_type, pattern in odds_patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    odds_data.extend([{
                        'type': odds_type,
                        'value': match,
                        'timestamp': screenshot_data['timestamp']
                    } for match in matches[:10]])  # Limit to 10 per type
            
        except Exception as e:
            print(f"❌ Odds extraction error: {e}")
        
        return odds_data
    
    def store_team_data(self, team, data, source):
        """Store team data in database"""
        try:
            cursor = self.matches_db.cursor()
            
            for match in data.get('matches', []):
                cursor.execute('''
                    INSERT INTO matches (team_home, team_away, score_home, score_away, 
                                       match_date, league, venue, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    match.get('home_team', ''),
                    match.get('away_team', ''),
                    match.get('home_score', 0),
                    match.get('away_score', 0),
                    match.get('match_date', datetime.now().isoformat()),
                    match.get('league', 'Unknown'),
                    match.get('venue', 'Unknown'),
                    source
                ))
            
            self.matches_db.commit()
            
        except Exception as e:
            print(f"❌ Database storage error: {e}")
    
    def store_team_analysis(self, team, analysis):
        """Store team analysis in database"""
        try:
            cursor = self.analysis_db.cursor()
            
            # Remove existing analysis for this team
            cursor.execute('DELETE FROM team_stats WHERE team_name = ?', (team,))
            
            # Insert new analysis
            cursor.execute('''
                INSERT INTO team_stats (team_name, analysis_data, patterns)
                VALUES (?, ?, ?)
            ''', (
                team,
                json.dumps(analysis, default=str),
                json.dumps(analysis.get('patterns', {}), default=str)
            ))
            
            self.analysis_db.commit()
            
        except Exception as e:
            print(f"❌ Analysis storage error: {e}")
    
    def store_bet9ja_data(self, bet9ja_result):
        """Store Bet9ja extracted data in database"""
        try:
            if not bet9ja_result or not isinstance(bet9ja_result, dict):
                print("⚠️ No valid Bet9ja data to store")
                return
            
            cursor = self.matches_db.cursor()
            
            # Store main match data
            teams = bet9ja_result.get('teams', {}) or {}
            live_score = bet9ja_result.get('live_score') or {}
            
            if teams.get('home_team') and teams.get('away_team'):
                cursor.execute('''
                    INSERT INTO matches (team_home, team_away, score_home, score_away, 
                                       match_date, league, venue, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    teams.get('home_team', 'Unknown'),
                    teams.get('away_team', 'Unknown'),
                    live_score.get('home', 0) if live_score else 0,
                    live_score.get('away', 0) if live_score else 0,
                    datetime.now().isoformat(),
                    teams.get('league', 'Bet9ja'),
                    'Bet9ja',
                    'BET9JA_EXTRACTOR'
                ))
                print(f"✅ Stored main match: {teams.get('home_team')} vs {teams.get('away_team')}")
            
            # Store historical matches if available
            historical_matches = bet9ja_result.get('historical_matches', []) or []
            stored_count = 0
            
            for match in historical_matches:
                if match and isinstance(match, dict):
                    cursor.execute('''
                        INSERT INTO matches (team_home, team_away, score_home, score_away, 
                                           match_date, league, venue, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        match.get('team', 'Unknown'),
                        'Opponent',
                        match.get('score1', 0),
                        match.get('score2', 0),
                        match.get('date', datetime.now().isoformat()),
                        'Historical',
                        'Bet9ja Historical',
                        'BET9JA_HISTORICAL'
                    ))
                    stored_count += 1
            
            self.matches_db.commit()
            print(f"✅ Stored Bet9ja data: {stored_count} historical matches")
            
        except Exception as e:
            print(f"❌ Bet9ja data storage error: {e}")
            import traceback
            traceback.print_exc()

    def store_prediction(self, prediction, bet9ja_data=None):
        """Store prediction in database"""
        try:
            cursor = self.analysis_db.cursor()
            
            # Create predictions table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    match_info TEXT,
                    predicted_score TEXT,
                    home_goals INTEGER,
                    away_goals INTEGER,
                    total_goals INTEGER,
                    result_prediction TEXT,
                    confidence REAL,
                    reasoning TEXT,
                    odds_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert prediction
            cursor.execute('''
                INSERT INTO predictions (match_info, predicted_score, home_goals, away_goals, 
                                       total_goals, result_prediction, confidence, reasoning, odds_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction.get('match', ''),
                prediction.get('predicted_score', ''),
                prediction.get('home_goals', 0),
                prediction.get('away_goals', 0),
                prediction.get('total_goals', 0),
                prediction.get('result', ''),
                prediction.get('confidence', 0),
                prediction.get('analysis', {}).get('reasoning', ''),
                json.dumps(bet9ja_data.get('current_odds', {}) if bet9ja_data else {}, default=str)
            ))
            
            self.analysis_db.commit()
            print(f"✅ Stored prediction: {prediction.get('predicted_score')} for {prediction.get('match')}")
            
        except Exception as e:
            print(f"❌ Prediction storage error: {e}")

    def store_comprehensive_analysis(self, analysis):
        """Store comprehensive team analysis in database"""
        try:
            cursor = self.analysis_db.cursor()
            
            # Create comprehensive analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS comprehensive_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    home_team TEXT,
                    away_team TEXT,
                    home_form TEXT,
                    away_form TEXT,
                    home_position INTEGER,
                    away_position INTEGER,
                    h2h_summary TEXT,
                    predictions TEXT,
                    analysis_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            match_info = analysis.get('match_info', {})
            home_analysis = analysis.get('home_team_analysis', {})
            away_analysis = analysis.get('away_team_analysis', {})
            h2h = analysis.get('head_to_head', {})
            predictions = analysis.get('predictions', {})
            
            # Insert analysis
            cursor.execute('''
                INSERT INTO comprehensive_analysis (
                    home_team, away_team, home_form, away_form, 
                    home_position, away_position, h2h_summary, 
                    predictions, analysis_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                match_info.get('home_team', ''),
                match_info.get('away_team', ''),
                json.dumps(home_analysis.get('current_form', {}), default=str),
                json.dumps(away_analysis.get('current_form', {}), default=str),
                home_analysis.get('league_position', {}).get('position', 0),
                away_analysis.get('league_position', {}).get('position', 0),
                json.dumps(h2h.get('summary', {}), default=str),
                json.dumps(predictions, default=str),
                json.dumps(analysis, default=str)
            ))
            
            self.analysis_db.commit()
            print(f"✅ Stored comprehensive analysis: {match_info.get('home_team')} vs {match_info.get('away_team')}")
            
        except Exception as e:
            print(f"❌ Comprehensive analysis storage error: {e}")

    def get_teams_count(self):
        """Get number of teams in database"""
        try:
            cursor = self.analysis_db.cursor()
            cursor.execute('SELECT COUNT(DISTINCT team_name) FROM team_stats')
            return cursor.fetchone()[0]
        except:
            return 0
    
    def get_matches_count(self):
        """Get number of matches in database"""
        try:
            cursor = self.matches_db.cursor()
            cursor.execute('SELECT COUNT(*) FROM matches')
            return cursor.fetchone()[0]
        except:
            return 0
    
    def get_last_mining_time(self):
        """Get last mining session time"""
        try:
            cursor = self.analysis_db.cursor()
            cursor.execute('SELECT MAX(last_updated) FROM team_stats')
            result = cursor.fetchone()[0]
            return result if result else 'Never'
        except:
            return 'Never'
    
    def run_server(self, host='localhost', port=5003):
        """Run the data mining bot server"""
        print(f"🤖 Sports Data Mining Bot starting...")
        print(f"📡 API Server: http://{host}:{port}")
        print(f"🗄️ Database: {self.get_teams_count()} teams, {self.get_matches_count()} matches")
        print("=" * 70)
        
        self.app.run(host=host, port=port, debug=False)

def main():
    """Main function"""
    bot = SportsDataMiningBot()
    
    print("🤖 Sports Data Mining Bot")
    print("=" * 70)
    print("✅ Features:")
    print("   📊 Comprehensive team data mining")
    print("   📸 Advanced screen monitoring")
    print("   🔍 Pattern analysis and predictions")
    print("   🗄️ SQLite database storage")
    print("   🤖 AI-powered change detection")
    print("   📈 Historical trend analysis")
    print("=" * 70)
    
    try:
        bot.run_server()
    except KeyboardInterrupt:
        print("\n🛑 Data mining bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")

if __name__ == "__main__":
    main()