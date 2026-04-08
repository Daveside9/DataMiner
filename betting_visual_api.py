#!/usr/bin/env python3
"""
DataMiner Pro - Betting Visual History API
Flask API backend for the betting visual history extractor
"""

import os
import sys
import json
import sqlite3
import threading
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
import logging

# Import the betting extractor
try:
    from betting_visual_history_extractor import BettingVisualHistoryExtractor, MatchResult
except ImportError:
    print("⚠️ Betting extractor not found, using mock implementation")
    BettingVisualHistoryExtractor = None
    MatchResult = None

app = Flask(__name__)
CORS(app)

# Global variables
active_extractions = {}
extraction_results = {}

class MockBettingExtractor:
    """Mock implementation for testing"""
    
    def __init__(self):
        self.logger = logging.getLogger('MockExtractor')
    
    def extract_betting_history(self, site_name, credentials=None):
        """Mock extraction that returns sample data"""
        import random
        import time
        
        teams = [
            'Manchester United', 'Liverpool', 'Chelsea', 'Arsenal', 'Manchester City',
            'Tottenham', 'Newcastle', 'Brighton', 'West Ham', 'Aston Villa'
        ]
        
        results = []
        num_matches = random.randint(5, 15)
        
        for i in range(num_matches):
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            home_score = random.randint(0, 4)
            away_score = random.randint(0, 4)
            
            # Simulate processing time
            time.sleep(0.5)
            
            result = type('MatchResult', (), {
                'match_id': f'mock_{i}',
                'date': '2024-01-15',
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'competition': 'Premier League',
                'betting_odds': {},
                'result_type': 'home_win' if home_score > away_score else 'away_win' if away_score > home_score else 'draw',
                'screenshot_path': f'screenshot_{i}.png',
                'confidence_score': 0.7 + random.random() * 0.3
            })()
            
            results.append(result)
        
        return results

@app.route('/')
def index():
    """Serve the main interface"""
    try:
        with open('frontend/betting-visual-extractor.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({'error': 'Frontend not found'}), 404

@app.route('/api/sites', methods=['GET'])
def get_supported_sites():
    """Get list of supported betting sites"""
    sites = [
        {
            'id': 'flashscore',
            'name': 'FlashScore',
            'url': 'https://www.flashscore.com',
            'login_required': False,
            'description': 'Live scores and results'
        },
        {
            'id': 'livescore',
            'name': 'LiveScore',
            'url': 'https://www.livescore.com',
            'login_required': False,
            'description': 'Football live scores'
        },
        {
            'id': 'bet365',
            'name': 'Bet365',
            'url': 'https://www.bet365.com',
            'login_required': True,
            'description': 'Sports betting and results'
        },
        {
            'id': 'bet9ja',
            'name': 'Bet9ja',
            'url': 'https://www.bet9ja.com',
            'login_required': False,
            'description': 'Nigerian sports betting'
        },
        {
            'id': 'betway',
            'name': 'Betway',
            'url': 'https://www.betway.com',
            'login_required': True,
            'description': 'International sports betting'
        }
    ]
    
    return jsonify({'sites': sites})

@app.route('/api/extract', methods=['POST'])
def start_extraction():
    """Start a new betting history extraction"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('site'):
            return jsonify({'error': 'Site is required'}), 400
        
        # Generate session ID
        session_id = f"session_{int(time.time())}"
        
        # Prepare extraction parameters
        extraction_params = {
            'site_name': data['site'],
            'max_matches': data.get('max_matches', 25),
            'ocr_engine': data.get('ocr_engine', 'easyocr'),
            'headless_mode': data.get('headless_mode', False),
            'save_screenshots': data.get('save_screenshots', True),
            'image_processing': {
                'enhance_contrast': data.get('enhance_contrast', True),
                'denoise': data.get('denoise', True),
                'sharpen': data.get('sharpen', True),
                'threshold': data.get('threshold', True)
            }
        }
        
        # Add credentials if provided
        credentials = None
        if data.get('username') and data.get('password'):
            credentials = {
                'username': data['username'],
                'password': data['password']
            }
        
        # Initialize extraction status
        active_extractions[session_id] = {
            'status': 'starting',
            'progress': 0,
            'message': 'Initializing extraction...',
            'start_time': datetime.now().isoformat(),
            'site_name': data['site'],
            'matches_found': 0,
            'errors': []
        }
        
        # Start extraction in background thread
        thread = threading.Thread(
            target=run_extraction,
            args=(session_id, extraction_params, credentials)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'session_id': session_id,
            'status': 'started',
            'message': 'Extraction started successfully'
        })
        
    except Exception as e:
        app.logger.error(f"Error starting extraction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<session_id>', methods=['GET'])
def get_extraction_status(session_id):
    """Get status of an extraction session"""
    if session_id not in active_extractions:
        return jsonify({'error': 'Session not found'}), 404
    
    status = active_extractions[session_id]
    
    # Add results if extraction is complete
    if session_id in extraction_results:
        status['results'] = extraction_results[session_id]
    
    return jsonify(status)

@app.route('/api/stop/<session_id>', methods=['POST'])
def stop_extraction(session_id):
    """Stop an active extraction"""
    if session_id not in active_extractions:
        return jsonify({'error': 'Session not found'}), 404
    
    # Mark extraction as stopped
    active_extractions[session_id]['status'] = 'stopped'
    active_extractions[session_id]['message'] = 'Extraction stopped by user'
    
    return jsonify({'message': 'Extraction stopped'})

@app.route('/api/results', methods=['GET'])
def get_all_results():
    """Get all extraction results from database"""
    try:
        conn = sqlite3.connect('betting_history.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT match_id, date, home_team, away_team, home_score, away_score,
                   competition, result_type, confidence_score, site_name, extracted_at
            FROM match_results
            ORDER BY extracted_at DESC
            LIMIT 100
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'match_id': row[0],
                'date': row[1],
                'home_team': row[2],
                'away_team': row[3],
                'home_score': row[4],
                'away_score': row[5],
                'competition': row[6],
                'result_type': row[7],
                'confidence_score': row[8],
                'site_name': row[9],
                'extracted_at': row[10]
            })
        
        conn.close()
        
        return jsonify({'results': results})
        
    except Exception as e:
        app.logger.error(f"Error getting results: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_extraction_stats():
    """Get extraction statistics"""
    try:
        conn = sqlite3.connect('betting_history.db')
        cursor = conn.cursor()
        
        # Total matches
        cursor.execute('SELECT COUNT(*) FROM match_results')
        total_matches = cursor.fetchone()[0]
        
        # Success rate (matches with confidence > 0.5)
        cursor.execute('SELECT COUNT(*) FROM match_results WHERE confidence_score > 0.5')
        successful_matches = cursor.fetchone()[0]
        success_rate = (successful_matches / total_matches * 100) if total_matches > 0 else 0
        
        # Average confidence
        cursor.execute('SELECT AVG(confidence_score) FROM match_results')
        avg_confidence = cursor.fetchone()[0] or 0
        avg_confidence = avg_confidence * 100
        
        # Sites count
        cursor.execute('SELECT COUNT(DISTINCT site_name) FROM match_results')
        sites_used = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_matches': total_matches,
            'success_rate': round(success_rate, 1),
            'avg_confidence': round(avg_confidence, 1),
            'sites_used': sites_used,
            'sites_supported': 5
        })
        
    except Exception as e:
        app.logger.error(f"Error getting stats: {e}")
        return jsonify({
            'total_matches': 0,
            'success_rate': 0,
            'avg_confidence': 0,
            'sites_used': 0,
            'sites_supported': 5
        })

@app.route('/api/screenshot/<filename>', methods=['GET'])
def get_screenshot(filename):
    """Serve screenshot files"""
    try:
        screenshot_path = Path('betting_screenshots') / filename
        if screenshot_path.exists():
            return send_file(screenshot_path)
        else:
            return jsonify({'error': 'Screenshot not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['GET'])
def export_results():
    """Export results to CSV"""
    try:
        import csv
        import io
        
        conn = sqlite3.connect('betting_history.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, home_team, away_team, home_score, away_score,
                   competition, result_type, confidence_score, site_name
            FROM match_results
            ORDER BY date DESC
        ''')
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Date', 'Home Team', 'Away Team', 'Home Score', 'Away Score',
            'Competition', 'Result Type', 'Confidence Score', 'Site Name'
        ])
        
        # Write data
        for row in cursor.fetchall():
            writer.writerow(row)
        
        conn.close()
        
        # Create response
        output.seek(0)
        return app.response_class(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=betting_history.csv'}
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_extraction(session_id, params, credentials):
    """Run extraction in background thread"""
    try:
        # Update status
        active_extractions[session_id]['status'] = 'running'
        active_extractions[session_id]['message'] = 'Starting browser...'
        active_extractions[session_id]['progress'] = 10
        
        # Initialize extractor
        if BettingVisualHistoryExtractor:
            extractor = BettingVisualHistoryExtractor()
        else:
            extractor = MockBettingExtractor()
        
        # Update status
        active_extractions[session_id]['message'] = 'Navigating to site...'
        active_extractions[session_id]['progress'] = 30
        
        # Run extraction
        results = extractor.extract_betting_history(
            params['site_name'],
            credentials
        )
        
        # Update status
        active_extractions[session_id]['message'] = 'Processing results...'
        active_extractions[session_id]['progress'] = 80
        
        # Convert results to JSON-serializable format
        json_results = []
        for result in results:
            json_results.append({
                'match_id': result.match_id if hasattr(result, 'match_id') else f'match_{len(json_results)}',
                'date': result.date if hasattr(result, 'date') else '2024-01-15',
                'home_team': result.home_team if hasattr(result, 'home_team') else 'Team A',
                'away_team': result.away_team if hasattr(result, 'away_team') else 'Team B',
                'home_score': result.home_score if hasattr(result, 'home_score') else 0,
                'away_score': result.away_score if hasattr(result, 'away_score') else 0,
                'competition': result.competition if hasattr(result, 'competition') else 'Unknown',
                'result_type': result.result_type if hasattr(result, 'result_type') else 'draw',
                'confidence_score': result.confidence_score if hasattr(result, 'confidence_score') else 0.8,
                'screenshot_path': result.screenshot_path if hasattr(result, 'screenshot_path') else None
            })
        
        # Store results
        extraction_results[session_id] = json_results
        
        # Update final status
        active_extractions[session_id]['status'] = 'completed'
        active_extractions[session_id]['message'] = f'Extraction completed! Found {len(results)} matches.'
        active_extractions[session_id]['progress'] = 100
        active_extractions[session_id]['matches_found'] = len(results)
        active_extractions[session_id]['end_time'] = datetime.now().isoformat()
        
    except Exception as e:
        # Update error status
        active_extractions[session_id]['status'] = 'error'
        active_extractions[session_id]['message'] = f'Extraction failed: {str(e)}'
        active_extractions[session_id]['errors'].append(str(e))
        app.logger.error(f"Extraction error for session {session_id}: {e}")

def init_database():
    """Initialize database if it doesn't exist"""
    try:
        conn = sqlite3.connect('betting_history.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_results (
                match_id TEXT PRIMARY KEY,
                date TEXT,
                home_team TEXT,
                away_team TEXT,
                home_score INTEGER,
                away_score INTEGER,
                competition TEXT,
                betting_odds TEXT,
                result_type TEXT,
                screenshot_path TEXT,
                confidence_score REAL,
                site_name TEXT,
                extracted_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extraction_sessions (
                session_id TEXT PRIMARY KEY,
                site_name TEXT,
                start_time TEXT,
                end_time TEXT,
                matches_extracted INTEGER,
                status TEXT,
                error_message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ Database initialized")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

def main():
    """Main function to run the API server"""
    print("🎯 Betting Visual History API Server")
    print("=" * 50)
    
    # Initialize database
    init_database()
    
    # Create directories
    Path('betting_screenshots').mkdir(exist_ok=True)
    Path('processed_images').mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Starting API server...")
    print("📊 Features available:")
    print("  ✅ Visual betting history extraction")
    print("  ✅ OCR-powered data extraction")
    print("  ✅ Multiple betting site support")
    print("  ✅ Real-time progress tracking")
    print("  ✅ Screenshot capture and analysis")
    print("  ✅ Database storage and export")
    print()
    print("🌐 Access the interface at: http://localhost:5003")
    print("📡 API endpoints available at: http://localhost:5003/api/")
    print()
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5003, debug=False, threaded=True)

if __name__ == "__main__":
    main()