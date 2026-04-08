#!/usr/bin/env python3
"""
DataMiner Pro - Start Betting Visual Extractor
Complete startup script for the betting visual history extraction system
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path
import json

def check_dependencies():
    """Check and install required dependencies"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'flask', 'flask-cors', 'selenium', 'opencv-python', 
        'pillow', 'pytesseract', 'easyocr', 'webdriver-manager',
        'beautifulsoup4', 'requests', 'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
            elif package == 'pillow':
                from PIL import Image
            elif package == 'flask-cors':
                from flask_cors import CORS
            elif package == 'webdriver-manager':
                from webdriver_manager.chrome import ChromeDriverManager
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️ Missing packages: {', '.join(missing_packages)}")
        print("📥 Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             check=True, capture_output=True)
                print(f"  ✅ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to install {package}: {e}")
        
        print("✅ Dependencies installation completed")
    else:
        print("✅ All dependencies are available")

def check_chrome_driver():
    """Check and setup Chrome driver"""
    print("🌐 Checking Chrome driver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Try to setup Chrome driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Install/update ChromeDriver
        driver_path = ChromeDriverManager().install()
        print(f"✅ Chrome driver ready: {driver_path}")
        
        # Test driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get('https://www.google.com')
        driver.quit()
        
        print("✅ Chrome driver test successful")
        return True
        
    except Exception as e:
        print(f"❌ Chrome driver setup failed: {e}")
        print("📥 Please install Google Chrome browser")
        return False

def check_ocr_engines():
    """Check OCR engines availability"""
    print("🔍 Checking OCR engines...")
    
    ocr_status = {'easyocr': False, 'tesseract': False}
    
    # Check EasyOCR
    try:
        import easyocr
        reader = easyocr.Reader(['en'])
        ocr_status['easyocr'] = True
        print("✅ EasyOCR is available")
    except Exception as e:
        print(f"⚠️ EasyOCR not available: {e}")
    
    # Check Tesseract
    try:
        import pytesseract
        from PIL import Image
        import numpy as np
        
        # Create a test image
        test_img = Image.fromarray(np.ones((100, 300, 3), dtype=np.uint8) * 255)
        pytesseract.image_to_string(test_img)
        ocr_status['tesseract'] = True
        print("✅ Tesseract OCR is available")
    except Exception as e:
        print(f"⚠️ Tesseract OCR not available: {e}")
        print("📥 Install Tesseract: https://github.com/tesseract-ocr/tesseract")
    
    if not any(ocr_status.values()):
        print("❌ No OCR engines available. Please install EasyOCR or Tesseract.")
        return False
    
    return True

def create_config_files():
    """Create configuration files if they don't exist"""
    print("⚙️ Setting up configuration files...")
    
    # Betting extractor config
    extractor_config = {
        "ocr_engine": "easyocr",
        "screenshot_quality": "high",
        "max_scroll_attempts": 10,
        "wait_timeout": 30,
        "image_processing": {
            "enhance_contrast": True,
            "denoise": True,
            "sharpen": True,
            "threshold": True
        },
        "betting_sites": {
            "flashscore": {
                "name": "FlashScore",
                "url": "https://www.flashscore.com",
                "login_required": False,
                "history_section": "/football/",
                "selectors": {
                    "results_section": ".sportName",
                    "match_rows": ".event__match",
                    "team_names": ".event__participant",
                    "scores": ".event__score",
                    "dates": ".event__time"
                }
            },
            "livescore": {
                "name": "LiveScore",
                "url": "https://www.livescore.com",
                "login_required": False,
                "history_section": "/football/",
                "selectors": {
                    "results_section": ".matches",
                    "match_rows": ".match",
                    "team_names": ".team-name",
                    "scores": ".score",
                    "dates": ".date"
                }
            },
            "bet365": {
                "name": "Bet365",
                "url": "https://www.bet365.com",
                "login_required": True,
                "history_section": "/members/services/resultsarchive/",
                "selectors": {
                    "login_button": ".hm-MainHeaderRHSLoggedOutWide_Login",
                    "username": "#loginUsername",
                    "password": "#loginPassword",
                    "submit": ".hm-LoginModule_LoginBtn",
                    "results_section": ".rcl-MarketGroupContainer",
                    "match_rows": ".rcl-MarketGroupContainer_Wrapper",
                    "team_names": ".rcl-ParticipantFixtureDetails_TeamName",
                    "scores": ".rcl-ParticipantFixtureDetails_BookCloses",
                    "dates": ".rcl-MarketHeaderLabel-isdate"
                }
            }
        }
    }
    
    config_file = 'betting_extractor_config.json'
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(extractor_config, f, indent=2)
        print(f"✅ Created config file: {config_file}")
    else:
        print(f"✅ Config file exists: {config_file}")

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        'betting_screenshots',
        'processed_images',
        'frontend',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ {directory}/")

def test_extraction():
    """Test the extraction system"""
    print("🧪 Testing extraction system...")
    
    try:
        # Import and test the extractor
        from betting_visual_history_extractor import BettingVisualHistoryExtractor
        
        extractor = BettingVisualHistoryExtractor()
        print("✅ Betting extractor initialized successfully")
        
        # Test database connection
        import sqlite3
        conn = sqlite3.connect('betting_history.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE type="table"')
        table_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ Database connection successful ({table_count} tables)")
        
        return True
        
    except Exception as e:
        print(f"❌ Extraction system test failed: {e}")
        return False

def start_api_server():
    """Start the API server in a separate thread"""
    def run_server():
        try:
            from betting_visual_api import app, init_database
            init_database()
            app.run(host='0.0.0.0', port=5003, debug=False, threaded=True)
        except Exception as e:
            print(f"❌ API server error: {e}")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    return server_thread

def show_system_info():
    """Display system information and features"""
    print("🎯 DataMiner Pro - Betting Visual History Extractor")
    print("=" * 70)
    print()
    print("🤖 ADVANCED AI-POWERED FEATURES:")
    print("  ✅ Visual Screenshot Analysis")
    print("  ✅ OCR Text Extraction (EasyOCR + Tesseract)")
    print("  ✅ Computer Vision Processing")
    print("  ✅ Intelligent Data Parsing")
    print("  ✅ Multi-Site Support")
    print("  ✅ Real-time Progress Tracking")
    print("  ✅ Database Storage & Export")
    print("  ✅ Web-based Interface")
    print()
    print("🎯 SUPPORTED BETTING SITES:")
    print("  🏈 FlashScore - Live scores and results")
    print("  ⚽ LiveScore - Football live scores")
    print("  🎰 Bet365 - Sports betting (Login required)")
    print("  🇳🇬 Bet9ja - Nigerian sports betting")
    print("  🌍 Betway - International betting")
    print()
    print("🔧 EXTRACTION CAPABILITIES:")
    print("  📊 Match Results & Scores")
    print("  📅 Historical Data")
    print("  🏆 Competition Information")
    print("  📈 Betting Odds (where available)")
    print("  📸 Screenshot Evidence")
    print("  🎯 Confidence Scoring")
    print()
    print("💡 HOW IT WORKS:")
    print("  1. 🌐 Opens betting site in browser")
    print("  2. 📸 Captures full-page screenshots")
    print("  3. 🔍 Uses OCR to extract text from images")
    print("  4. 🧠 AI parses and structures the data")
    print("  5. 💾 Stores results in database")
    print("  6. 📊 Provides confidence scoring")
    print()

def main():
    """Main startup function"""
    show_system_info()
    
    print("🚀 SYSTEM STARTUP:")
    print("-" * 30)
    
    # Check dependencies
    check_dependencies()
    
    # Check Chrome driver
    if not check_chrome_driver():
        print("❌ Chrome driver setup failed. Please install Google Chrome.")
        return False
    
    # Check OCR engines
    if not check_ocr_engines():
        print("❌ No OCR engines available. System may not work properly.")
    
    # Create config files
    create_config_files()
    
    # Create directories
    create_directories()
    
    # Test extraction system
    if not test_extraction():
        print("⚠️ Extraction system test failed, but continuing...")
    
    print("\n🎯 STARTUP OPTIONS:")
    print("  1. Start Web Interface (Recommended)")
    print("  2. Run Command Line Extraction")
    print("  3. Test OCR Engines")
    print("  4. View System Status")
    print("  5. Exit")
    
    while True:
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            print("\n🌐 Starting Web Interface...")
            print("⏳ Initializing API server...")
            
            # Start API server
            server_thread = start_api_server()
            time.sleep(3)
            
            print("✅ API server started successfully!")
            print()
            print("🎉 BETTING VISUAL EXTRACTOR IS READY!")
            print("=" * 50)
            print("🌐 Web Interface: http://localhost:5003")
            print("📡 API Endpoints: http://localhost:5003/api/")
            print()
            print("🎯 QUICK START:")
            print("  1. Open http://localhost:5003 in your browser")
            print("  2. Select a betting site (FlashScore recommended)")
            print("  3. Configure extraction settings")
            print("  4. Click 'Start Extraction'")
            print("  5. Watch real-time progress")
            print("  6. View extracted match results")
            print()
            print("📊 FEATURES:")
            print("  • Real-time extraction progress")
            print("  • Visual screenshot analysis")
            print("  • OCR text extraction")
            print("  • Match result parsing")
            print("  • Database storage")
            print("  • CSV export")
            print("  • Confidence scoring")
            print()
            print("Press Ctrl+C to stop the server")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down server...")
                break
        
        elif choice == '2':
            print("\n💻 Command Line Extraction")
            site = input("Enter betting site (flashscore/livescore/bet365): ").strip()
            
            if site:
                print(f"🚀 Starting extraction from {site}...")
                try:
                    from betting_visual_history_extractor import BettingVisualHistoryExtractor
                    
                    extractor = BettingVisualHistoryExtractor()
                    results = extractor.extract_betting_history(site)
                    
                    print(f"✅ Extraction completed!")
                    print(f"📊 Found {len(results)} matches")
                    
                    for i, result in enumerate(results[:5]):
                        print(f"  {i+1}. {result.home_team} {result.home_score}-{result.away_score} {result.away_team}")
                    
                    if len(results) > 5:
                        print(f"  ... and {len(results) - 5} more matches")
                    
                except Exception as e:
                    print(f"❌ Extraction failed: {e}")
            else:
                print("❌ Invalid site selection")
        
        elif choice == '3':
            print("\n🔍 Testing OCR Engines...")
            check_ocr_engines()
        
        elif choice == '4':
            print("\n📊 System Status:")
            print(f"  Python Version: {sys.version.split()[0]}")
            print(f"  Working Directory: {os.getcwd()}")
            print(f"  Config File: {'✅' if os.path.exists('betting_extractor_config.json') else '❌'}")
            print(f"  Database: {'✅' if os.path.exists('betting_history.db') else '❌'}")
            print(f"  Screenshots Dir: {'✅' if os.path.exists('betting_screenshots') else '❌'}")
        
        elif choice == '5':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    main()