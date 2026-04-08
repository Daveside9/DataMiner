#!/usr/bin/env python3
"""
Improved Visual Betting Site Monitor
Enhanced screenshot functionality with better quality and user experience
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

class ImprovedVisualMonitor:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.monitoring_active = False
        self.screenshots = []
        self.changes_detected = []
        self.current_odds = {}
        self.setup_routes()
        
        # Create directories
        os.makedirs('screenshots', exist_ok=True)
        os.makedirs('screenshots/thumbnails', exist_ok=True)
    
    def setup_routes(self):
        """Setup Flask routes for improved visual monitoring"""
        
        @self.app.route('/api/start-visual-monitoring', methods=['POST'])
        def start_visual_monitoring():
            data = request.get_json()
            url = data.get('url')
            interval = data.get('interval', 30)
            duration = data.get('duration', 10)
            
            if self.monitoring_active:
                return jsonify({'error': 'Visual monitoring already active'}), 400
            
            thread = threading.Thread(
                target=self.start_improved_monitoring,
                args=(url, interval, duration)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'message': f'Started improved visual monitoring of {url}',
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
            limit = request.args.get('limit', 10, type=int)
            return jsonify({
                'screenshots': self.screenshots[-limit:],
                'changes': self.changes_detected[-5:],
                'total_screenshots': len(self.screenshots),
                'total_changes': len(self.changes_detected)
            })
        
        @self.app.route('/api/live-preview', methods=['GET'])
        def get_live_preview():
            if not self.screenshots:
                return jsonify({'error': 'No screenshots available'}), 404
            
            latest = self.screenshots[-1]
            return jsonify({
                'screenshot': latest,
                'monitoring_active': self.monitoring_active
            })
        
        @self.app.route('/screenshot/<filename>')
        def serve_screenshot(filename):
            try:
                return send_file(f'screenshots/{filename}')
            except:
                return send_file(f'screenshots/thumbnails/{filename}')
    
    def start_improved_monitoring(self, url, interval, duration):
        """Start improved visual monitoring with better screenshot quality"""
        print(f"📸 Starting IMPROVED visual monitoring of {url}")
        print(f"⏱️ Interval: {interval}s, Duration: {duration}min")
        
        self.monitoring_active = True
        start_time = time.time()
        end_time = start_time + (duration * 60)
        
        # Enhanced Chrome options for better screenshots
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        driver = None
        previous_screenshot = None
        
        try:
            driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Set window size explicitly
            driver.set_window_size(1920, 1080)
            
            while self.monitoring_active and time.time() < end_time:
                try:
                    timestamp = datetime.now()
                    print(f"📸 {timestamp.strftime('%H:%M:%S')} - Taking IMPROVED screenshot...")
                    
                    # Load page with better handling
                    driver.get(url)
                    time.sleep(8)  # Wait longer for full page load
                    
                    # Wait for page to be ready
                    driver.execute_script("return document.readyState") == "complete"
                    
                    # Scroll to ensure all content is loaded
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(2)
                    
                    # Take high-quality screenshot
                    screenshot_filename = f"improved_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
                    screenshot_path = f"screenshots/{screenshot_filename}"
                    
                    # Take screenshot with error handling
                    success = driver.save_screenshot(screenshot_path)
                    
                    if not success or not os.path.exists(screenshot_path):
                        print(f"❌ Screenshot failed, retrying...")
                        time.sleep(3)
                        driver.save_screenshot(screenshot_path)
                    
                    # Verify and enhance screenshot
                    if os.path.exists(screenshot_path):
                        file_size = os.path.getsize(screenshot_path)
                        print(f"📊 Screenshot size: {file_size} bytes")
                        
                        # Create thumbnail for faster loading
                        thumbnail_path = self.create_improved_thumbnail(screenshot_path)
                        
                        # Enhanced analysis
                        analysis = self.analyze_improved_screenshot(driver, screenshot_path)
                        
                        screenshot_data = {
                            'timestamp': timestamp.isoformat(),
                            'filename': screenshot_filename,
                            'thumbnail': thumbnail_path,
                            'url': url,
                            'analysis': analysis,
                            'file_size': file_size,
                            'page_title': analysis.get('page_title', 'Unknown'),
                            'quality': 'excellent' if file_size > 200000 else 'good'
                        }
                        
                        self.screenshots.append(screenshot_data)
                        
                        # Detect changes
                        if previous_screenshot and os.path.exists(screenshot_path):
                            changes = self.detect_improved_changes(previous_screenshot, screenshot_path)
                            if changes:
                                change_data = {
                                    'timestamp': timestamp.isoformat(),
                                    'changes': changes,
                                    'screenshot': screenshot_filename
                                }
                                self.changes_detected.append(change_data)
                                print(f"🔄 Changes detected: {len(changes)} differences")
                        
                        previous_screenshot = screenshot_path
                        
                        # Update odds
                        if analysis.get('odds'):
                            self.current_odds = {
                                'timestamp': timestamp.isoformat(),
                                'odds_data': analysis['odds'],
                                'total_odds': analysis.get('odds_found', 0)
                            }
                        
                        print(f"✅ IMPROVED screenshot saved: {screenshot_filename}")
                        print(f"📊 Analysis: {analysis.get('odds_found', 0)} odds, {analysis.get('elements_count', 0)} elements")
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    print(f"❌ Screenshot error: {e}")
                    time.sleep(interval)
        
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
        
        finally:
            if driver:
                driver.quit()
            self.monitoring_active = False
            print("✅ IMPROVED visual monitoring completed!")
    
    def create_improved_thumbnail(self, screenshot_path):
        """Create high-quality thumbnail"""
        try:
            with Image.open(screenshot_path) as img:
                # Create larger thumbnail for better quality
                img.thumbnail((600, 400), Image.Resampling.LANCZOS)
                
                # Add timestamp overlay
                draw = ImageDraw.Draw(img)
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                # Try to use a better font
                try:
                    font = ImageFont.truetype("arial.ttf", 16)
                except:
                    font = ImageFont.load_default()
                
                # Add semi-transparent background for text
                text_bbox = draw.textbbox((0, 0), timestamp, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # Draw background rectangle
                draw.rectangle([10, 10, 10 + text_width + 10, 10 + text_height + 10], 
                             fill=(0, 0, 0, 128))
                
                # Draw timestamp
                draw.text((15, 15), timestamp, fill=(255, 255, 255), font=font)
                
                # Save thumbnail
                thumbnail_filename = f"thumb_{os.path.basename(screenshot_path)}"
                thumbnail_path = f"screenshots/thumbnails/{thumbnail_filename}"
                img.save(thumbnail_path, "PNG", optimize=True, quality=95)
                
                return f"thumbnails/{thumbnail_filename}"
        except Exception as e:
            print(f"❌ Thumbnail creation error: {e}")
            return None
    
    def analyze_improved_screenshot(self, driver, screenshot_path):
        """Enhanced screenshot analysis"""
        analysis = {
            'odds_found': 0,
            'matches_visible': 0,
            'live_indicators': {},
            'odds': {},
            'text_content': '',
            'page_title': '',
            'elements_count': 0,
            'page_loaded': True
        }
        
        try:
            # Get page info
            analysis['page_title'] = driver.title
            page_text = driver.find_element(By.TAG_NAME, "body").text
            analysis['text_content'] = page_text[:2000]  # More text for better analysis
            
            # Enhanced odds detection
            import re
            odds_patterns = {
                'decimal': r'\b[1-9]\.\d{2}\b',
                'fractional': r'\b\d+/\d+\b',
                'american_plus': r'\+\d{3,4}\b',
                'american_minus': r'-\d{3,4}\b'
            }
            
            all_odds = {}
            for odds_type, pattern in odds_patterns.items():
                odds = re.findall(pattern, page_text)
                if odds:
                    all_odds[odds_type] = list(set(odds))[:15]  # Unique odds, limit 15
            
            analysis['odds'] = all_odds
            analysis['odds_found'] = sum(len(odds) for odds in all_odds.values())
            
            # Enhanced live detection
            live_patterns = {
                'live_caps': r'\bLIVE\b',
                'live_normal': r'\bLive\b',
                'minute_marker': r"'\d{1,2}",
                'time_format': r'\b\d{1,2}:\d{2}\b',
                'match_status': r'\bHT\b|\bFT\b',
                'in_play': r'\bIn-Play\b'
            }
            
            live_indicators = {}
            for indicator_type, pattern in live_patterns.items():
                matches = re.findall(pattern, page_text)
                if matches:
                    live_indicators[indicator_type] = len(matches)
            
            analysis['live_indicators'] = live_indicators
            
            # Count page elements
            try:
                all_elements = driver.find_elements(By.XPATH, "//*")
                analysis['elements_count'] = len(all_elements)
                
                # Check if page loaded properly
                if len(all_elements) < 10:
                    analysis['page_loaded'] = False
                    
            except Exception as e:
                analysis['elements_count'] = 0
                analysis['page_loaded'] = False
            
            # Estimate matches
            match_indicators = len(re.findall(r'\bvs\b|\bv\b', page_text, re.IGNORECASE))
            analysis['matches_visible'] = min(match_indicators, 50)
            
        except Exception as e:
            print(f"❌ Enhanced analysis error: {e}")
            analysis['page_loaded'] = False
        
        return analysis
    
    def detect_improved_changes(self, old_screenshot, new_screenshot):
        """Improved change detection"""
        changes = []
        
        try:
            from PIL import Image, ImageChops
            
            img1 = Image.open(old_screenshot)
            img2 = Image.open(new_screenshot)
            
            # Ensure same size
            if img1.size != img2.size:
                img2 = img2.resize(img1.size)
            
            # Calculate difference
            diff = ImageChops.difference(img1, img2)
            diff_gray = diff.convert('L')
            histogram = diff_gray.histogram()
            
            # More sophisticated change detection
            total_pixels = sum(histogram)
            changed_pixels = sum(histogram[1:])
            
            if total_pixels > 0:
                change_percentage = (changed_pixels / total_pixels) * 100
                
                if change_percentage > 0.5:  # More sensitive detection
                    changes.append({
                        'type': 'visual_change',
                        'percentage': round(change_percentage, 2),
                        'description': f'{change_percentage:.1f}% of image changed',
                        'severity': 'high' if change_percentage > 10 else 'medium' if change_percentage > 5 else 'low'
                    })
                    
                    # Detect significant changes
                    if change_percentage > 20:
                        changes.append({
                            'type': 'major_change',
                            'description': 'Major page changes detected - possible odds update'
                        })
            
        except Exception as e:
            print(f"❌ Change detection error: {e}")
        
        return changes
    
    def run_server(self, host='localhost', port=5002):
        """Run the improved visual monitoring server"""
        print(f"📸 IMPROVED Visual Bet Monitor starting...")
        print(f"📡 API Server: http://{host}:{port}")
        print(f"🌐 Enhanced Features: High-quality screenshots, Better thumbnails, Improved analysis")
        print("=" * 70)
        
        self.app.run(host=host, port=port, debug=False)

def main():
    """Main function"""
    monitor = ImprovedVisualMonitor()
    
    print("📸 IMPROVED Visual Betting Site Monitor")
    print("=" * 70)
    print("✅ Enhanced Features:")
    print("   📸 High-quality screenshot capture")
    print("   🖼️ Improved thumbnail generation")
    print("   🔍 Better change detection")
    print("   📊 Enhanced odds analysis")
    print("   ⚡ Faster loading and display")
    print("   🎯 More reliable monitoring")
    print("=" * 70)
    
    try:
        monitor.run_server()
    except KeyboardInterrupt:
        print("\n🛑 Improved visual monitor stopped by user")
    except Exception as e:
        print(f"❌ Monitor error: {e}")

if __name__ == "__main__":
    main()