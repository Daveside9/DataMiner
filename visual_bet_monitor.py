#!/usr/bin/env python3
"""
Visual Betting Site Monitor
Monitor betting sites with visual screenshots and change detection
"""

import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import threading
import json

class VisualBetMonitor:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.monitoring_active = False
        self.screenshots = []
        self.changes_detected = []
        self.current_odds = {}
        self.setup_routes()
        
        # Create screenshots directory
        os.makedirs('screenshots', exist_ok=True)
    
    def setup_routes(self):
        """Setup Flask routes for visual monitoring"""
        
        @self.app.route('/api/start-visual-monitoring', methods=['POST'])
        def start_visual_monitoring():
            data = request.get_json()
            url = data.get('url')
            interval = data.get('interval', 30)  # seconds
            duration = data.get('duration', 10)  # minutes
            
            if self.monitoring_active:
                return jsonify({'error': 'Visual monitoring already active'}), 400
            
            # Start visual monitoring in background
            thread = threading.Thread(
                target=self.start_visual_monitoring_process,
                args=(url, interval, duration)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'message': f'Started visual monitoring of {url}',
                'interval': interval,
                'duration': duration
            })
        
        @self.app.route('/api/stop-visual-monitoring', methods=['POST'])
        def stop_visual_monitoring():
            self.monitoring_active = False
            return jsonify({'success': True, 'message': 'Visual monitoring stopped'})
        
        @self.app.route('/api/visual-status', methods=['GET'])
        def get_visual_status():
            return jsonify({
                'monitoring_active': self.monitoring_active,
                'screenshots_count': len(self.screenshots),
                'changes_detected': len(self.changes_detected),
                'latest_screenshot': self.screenshots[-1] if self.screenshots else None,
                'current_odds': self.current_odds
            })
        
        @self.app.route('/api/screenshots', methods=['GET'])
        def get_screenshots():
            # Get query parameters
            limit = request.args.get('limit', 10, type=int)
            include_analysis = request.args.get('analysis', 'true').lower() == 'true'
            
            recent_screenshots = self.screenshots[-limit:] if self.screenshots else []
            recent_changes = self.changes_detected[-5:] if self.changes_detected else []
            
            # Prepare response data
            response_data = {
                'screenshots': recent_screenshots,
                'changes': recent_changes,
                'total_screenshots': len(self.screenshots),
                'total_changes': len(self.changes_detected),
                'monitoring_active': self.monitoring_active
            }
            
            # Add summary statistics
            if recent_screenshots:
                latest = recent_screenshots[-1]
                response_data['latest_analysis'] = latest.get('analysis', {})
                response_data['latest_quality'] = latest.get('quality', 'unknown')
                response_data['latest_size'] = latest.get('file_size', 0)
            
            return jsonify(response_data)
        
        @self.app.route('/api/live-preview', methods=['GET'])
        def get_live_preview():
            """Get the most recent screenshot for live preview"""
            if not self.screenshots:
                return jsonify({'error': 'No screenshots available'}), 404
            
            latest = self.screenshots[-1]
            return jsonify({
                'screenshot': latest,
                'monitoring_active': self.monitoring_active,
                'next_capture_in': 30 if self.monitoring_active else None  # Approximate
            })
        
        @self.app.route('/screenshot/<filename>')
        def serve_screenshot(filename):
            return send_file(f'screenshots/{filename}')
    
    def start_visual_monitoring_process(self, url, interval, duration):
        """Start the visual monitoring process"""
        print(f"📸 Starting visual monitoring of {url}")
        print(f"⏱️ Interval: {interval}s, Duration: {duration}min")
        
        self.monitoring_active = True
        start_time = time.time()
        end_time = start_time + (duration * 60)
        
        # Setup Chrome for screenshots
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = None
        previous_screenshot = None
        
        try:
            driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            while self.monitoring_active and time.time() < end_time:
                try:
                    timestamp = datetime.now()
                    print(f"📸 {timestamp.strftime('%H:%M:%S')} - Taking screenshot...")
                    
                    # Load the page with better error handling
                    driver.get(url)
                    time.sleep(5)  # Wait longer for page to load
                    
                    # Wait for page to be fully loaded
                    driver.execute_script("return document.readyState") == "complete"
                    
                    # Scroll to capture more content
                    driver.execute_script("window.scrollTo(0, 0);")  # Scroll to top
                    time.sleep(1)
                    
                    # Take screenshot with better filename
                    screenshot_filename = f"bet_monitor_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
                    screenshot_path = f"screenshots/{screenshot_filename}"
                    
                    # Take full page screenshot
                    success = driver.save_screenshot(screenshot_path)
                    
                    if not success or not os.path.exists(screenshot_path):
                        print(f"❌ Screenshot failed for {url}")
                        continue
                    
                    # Verify screenshot was created and has reasonable size
                    file_size = os.path.getsize(screenshot_path)
                    if file_size < 10000:  # Less than 10KB indicates problem
                        print(f"⚠️ Screenshot too small ({file_size} bytes), retrying...")
                        time.sleep(2)
                        driver.save_screenshot(screenshot_path)
                        file_size = os.path.getsize(screenshot_path)
                    
                    # Analyze the screenshot with enhanced detection
                    analysis = self.analyze_betting_screenshot(driver, screenshot_path)
                    
                    # Create thumbnail for faster loading
                    thumbnail_path = self.create_thumbnail(screenshot_path)
                    
                    screenshot_data = {
                        'timestamp': timestamp.isoformat(),
                        'filename': screenshot_filename,
                        'thumbnail': thumbnail_path,
                        'url': url,
                        'analysis': analysis,
                        'file_size': file_size,
                        'page_title': analysis.get('page_title', 'Unknown'),
                        'quality': analysis.get('screenshot_quality', 'unknown')
                    }
                    
                    self.screenshots.append(screenshot_data)
                    
                    # Compare with previous screenshot for changes
                    if previous_screenshot and os.path.exists(screenshot_path):
                        changes = self.detect_visual_changes(previous_screenshot, screenshot_path)
                        if changes:
                            change_data = {
                                'timestamp': timestamp.isoformat(),
                                'changes': changes,
                                'screenshot': screenshot_filename,
                                'previous_screenshot': os.path.basename(previous_screenshot)
                            }
                            self.changes_detected.append(change_data)
                            print(f"🔄 Changes detected: {len(changes)} differences")
                    
                    previous_screenshot = screenshot_path
                    
                    # Update current odds if found
                    if analysis.get('odds'):
                        self.current_odds.update({
                            'timestamp': timestamp.isoformat(),
                            'odds_data': analysis['odds'],
                            'total_odds': analysis.get('odds_found', 0)
                        })
                    
                    print(f"✅ Screenshot saved: {screenshot_filename} ({file_size} bytes)")
                    print(f"📊 Analysis: {analysis.get('odds_found', 0)} odds, {len(analysis.get('elements_detected', []))} elements")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"❌ Screenshot error: {e}")
                    time.sleep(interval)
        
        except Exception as e:
            print(f"❌ Visual monitoring error: {e}")
        
        finally:
            if driver:
                driver.quit()
            self.monitoring_active = False
            print("✅ Visual monitoring completed!")
    
    def analyze_betting_screenshot(self, driver, screenshot_path):
        """Analyze screenshot for betting information with enhanced detection"""
        analysis = {
            'odds_found': 0,
            'matches_visible': 0,
            'live_indicators': 0,
            'odds': {},
            'text_content': '',
            'page_title': '',
            'screenshot_quality': 'good',
            'elements_detected': []
        }
        
        try:
            # Get page title
            analysis['page_title'] = driver.title
            
            # Get page text content
            page_text = driver.find_element(By.TAG_NAME, "body").text
            analysis['text_content'] = page_text[:1000]  # First 1000 chars
            
            # Enhanced odds detection
            import re
            odds_patterns = [
                (r'\b\d+\.\d{2}\b', 'decimal'),     # Decimal odds like 2.50
                (r'\b\d+/\d+\b', 'fractional'),     # Fractional odds like 5/2
                (r'\+\d{3,4}\b', 'american_plus'),  # American odds like +150
                (r'-\d{3,4}\b', 'american_minus'),  # American odds like -150
                (r'\b[12]\.\d{1,2}\b', 'low_decimal') # Low decimal odds
            ]
            
            all_odds = {}
            for pattern, odds_type in odds_patterns:
                odds = re.findall(pattern, page_text)
                if odds:
                    all_odds[odds_type] = odds[:10]  # Limit to 10 per type
            
            analysis['odds'] = all_odds
            analysis['odds_found'] = sum(len(odds) for odds in all_odds.values())
            
            # Enhanced live indicators
            live_patterns = [
                (r'\bLIVE\b', 'live_caps'),
                (r'\bLive\b', 'live_normal'),
                (r"'\d{1,2}", 'minute_marker'),
                (r'\b\d{1,2}:\d{2}\b', 'time_format'),
                (r'\bHT\b|\bFT\b', 'match_status'),
                (r'\bIn-Play\b', 'in_play')
            ]
            
            live_indicators = {}
            for pattern, indicator_type in live_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    live_indicators[indicator_type] = len(matches)
            
            analysis['live_indicators'] = live_indicators
            
            # Detect specific elements
            elements_detected = []
            
            # Try to find common betting site elements
            try:
                # Look for match elements
                match_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'vs') or contains(text(), 'v ')]")
                if match_elements:
                    elements_detected.append(f"Found {len(match_elements)} match elements")
                
                # Look for odds elements
                odds_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'odd') or contains(@class, 'price')]")
                if odds_elements:
                    elements_detected.append(f"Found {len(odds_elements)} odds elements")
                
                # Look for live elements
                live_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'LIVE') or contains(text(), 'Live')]")
                if live_elements:
                    elements_detected.append(f"Found {len(live_elements)} live elements")
                    
            except Exception as e:
                elements_detected.append(f"Element detection error: {str(e)[:50]}")
            
            analysis['elements_detected'] = elements_detected
            analysis['matches_visible'] = len([e for e in elements_detected if 'match' in e.lower()])
            
            # Check screenshot quality
            if os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                if file_size < 50000:  # Less than 50KB
                    analysis['screenshot_quality'] = 'poor'
                elif file_size > 500000:  # More than 500KB
                    analysis['screenshot_quality'] = 'excellent'
                else:
                    analysis['screenshot_quality'] = 'good'
            
        except Exception as e:
            print(f"❌ Enhanced analysis error: {e}")
            analysis['elements_detected'].append(f"Analysis error: {str(e)[:50]}")
        
        return analysis
    
    def detect_visual_changes(self, old_screenshot, new_screenshot):
        """Detect visual changes between screenshots"""
        changes = []
        
        try:
            from PIL import Image, ImageChops
            
            # Open images
            img1 = Image.open(old_screenshot)
            img2 = Image.open(new_screenshot)
            
            # Resize to same size if needed
            if img1.size != img2.size:
                img2 = img2.resize(img1.size)
            
            # Calculate difference
            diff = ImageChops.difference(img1, img2)
            
            # Convert to grayscale and get histogram
            diff_gray = diff.convert('L')
            histogram = diff_gray.histogram()
            
            # Calculate change percentage
            total_pixels = sum(histogram)
            changed_pixels = sum(histogram[1:])  # Exclude pixels with 0 difference
            
            if total_pixels > 0:
                change_percentage = (changed_pixels / total_pixels) * 100
                
                if change_percentage > 1:  # More than 1% change
                    changes.append({
                        'type': 'visual_change',
                        'percentage': round(change_percentage, 2),
                        'description': f'{change_percentage:.1f}% of image changed'
                    })
            
        except Exception as e:
            print(f"❌ Change detection error: {e}")
        
        return changes
    
    def create_thumbnail(self, screenshot_path):
        """Create a thumbnail version of the screenshot for faster loading"""
        try:
            from PIL import Image
            
            # Open the original image
            with Image.open(screenshot_path) as img:
                # Create thumbnail (max 400x300)
                img.thumbnail((400, 300), Image.Resampling.LANCZOS)
                
                # Save thumbnail
                thumbnail_filename = f"thumb_{os.path.basename(screenshot_path)}"
                thumbnail_path = f"screenshots/{thumbnail_filename}"
                img.save(thumbnail_path, "PNG", optimize=True)
                
                return thumbnail_filename
        except Exception as e:
            print(f"❌ Thumbnail creation error: {e}")
            return None
    
    def run_server(self, host='localhost', port=5002):
        """Run the visual monitoring server"""
        print(f"📸 Visual Bet Monitor starting...")
        print(f"📡 API Server: http://{host}:{port}")
        print(f"🌐 Features: Screenshot monitoring, Change detection, Odds tracking")
        print("=" * 60)
        
        self.app.run(host=host, port=port, debug=False)

def main():
    """Main function"""
    monitor = VisualBetMonitor()
    
    print("📸 Visual Betting Site Monitor")
    print("=" * 60)
    print("✅ Features:")
    print("   📸 Automatic screenshot capture")
    print("   🔄 Visual change detection")
    print("   📊 Odds extraction and tracking")
    print("   ⏱️ Customizable monitoring intervals")
    print("   🎯 Live betting site analysis")
    print("=" * 60)
    
    try:
        monitor.run_server()
    except KeyboardInterrupt:
        print("\n🛑 Visual monitor stopped by user")
    except Exception as e:
        print(f"❌ Monitor error: {e}")

if __name__ == "__main__":
    main()