#!/usr/bin/env python3
"""
DataMiner Pro - Betting Visual History Extractor
Advanced system to extract visual history results from betting sites
Uses computer vision, OCR, and intelligent navigation
"""

import os
import sys
import time
import json
import cv2
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
import logging

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Computer Vision and OCR
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    import easyocr
except ImportError:
    print("⚠️ OCR libraries not installed. Run: pip install pytesseract pillow easyocr")

# Image processing
try:
    import cv2
    import numpy as np
except ImportError:
    print("⚠️ OpenCV not installed. Run: pip install opencv-python")

@dataclass
class MatchResult:
    """Represents a historical match result"""
    match_id: str
    date: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    competition: str
    betting_odds: Dict[str, float]
    result_type: str  # 'home_win', 'away_win', 'draw'
    screenshot_path: Optional[str] = None
    confidence_score: float = 0.0

@dataclass
class BettingSite:
    """Configuration for a betting site"""
    name: str
    url: str
    login_required: bool
    selectors: Dict[str, str]
    navigation_steps: List[Dict[str, Any]]
    ocr_regions: List[Dict[str, Any]]

class BettingVisualHistoryExtractor:
    """Main class for extracting visual betting history"""
    
    def __init__(self, config_file: str = "betting_extractor_config.json"):
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.init_database()
        self.init_ocr()
        self.driver = None
        
        # Create directories
        self.screenshots_dir = Path("betting_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
        self.processed_dir = Path("processed_images")
        self.processed_dir.mkdir(exist_ok=True)
        
        self.logger.info("🎯 Betting Visual History Extractor initialized")

    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('betting_extractor.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('BettingExtractor')

    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration"""
        default_config = {
            "ocr_engine": "easyocr",  # or "tesseract"
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
                },
                "bet9ja": {
                    "name": "Bet9ja",
                    "url": "https://www.bet9ja.com",
                    "login_required": False,
                    "history_section": "/sport/football",
                    "selectors": {
                        "results_section": ".sport-category",
                        "match_rows": ".match-row",
                        "team_names": ".team-name",
                        "scores": ".match-score",
                        "dates": ".match-date"
                    }
                }
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Error loading config: {e}")
        
        return default_config

    def init_database(self):
        """Initialize database for storing results"""
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

    def init_ocr(self):
        """Initialize OCR engines"""
        try:
            if self.config['ocr_engine'] == 'easyocr':
                self.ocr_reader = easyocr.Reader(['en'])
                self.logger.info("✅ EasyOCR initialized")
            else:
                # Configure Tesseract path if needed
                # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                self.logger.info("✅ Tesseract OCR configured")
        except Exception as e:
            self.logger.error(f"❌ OCR initialization failed: {e}")

    def setup_driver(self, headless: bool = False) -> webdriver.Chrome:
        """Setup Chrome driver with optimal settings"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # Optimize for betting sites
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent to avoid detection
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Set window size for consistent screenshots
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    def login_to_site(self, site_config: Dict[str, Any], credentials: Dict[str, str]) -> bool:
        """Login to betting site if required"""
        if not site_config.get('login_required', False):
            return True
        
        try:
            self.logger.info(f"🔐 Logging into {site_config['name']}...")
            
            # Navigate to login
            self.driver.get(site_config['url'])
            time.sleep(3)
            
            # Click login button
            login_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, site_config['selectors']['login_button']))
            )
            login_btn.click()
            time.sleep(2)
            
            # Enter credentials
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, site_config['selectors']['username']))
            )
            username_field.send_keys(credentials['username'])
            
            password_field = self.driver.find_element(By.CSS_SELECTOR, site_config['selectors']['password'])
            password_field.send_keys(credentials['password'])
            
            # Submit login
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, site_config['selectors']['submit'])
            submit_btn.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "login" not in self.driver.current_url.lower():
                self.logger.info("✅ Login successful")
                return True
            else:
                self.logger.error("❌ Login failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Login error: {e}")
            return False

    def navigate_to_history_section(self, site_config: Dict[str, Any]) -> bool:
        """Navigate to the betting history/results section"""
        try:
            history_url = site_config['url'] + site_config.get('history_section', '')
            self.logger.info(f"📍 Navigating to history section: {history_url}")
            
            self.driver.get(history_url)
            time.sleep(5)
            
            # Wait for results section to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, site_config['selectors']['results_section']))
            )
            
            self.logger.info("✅ History section loaded")
            return True
            
        except TimeoutException:
            self.logger.error("❌ History section not found or took too long to load")
            return False
        except Exception as e:
            self.logger.error(f"❌ Navigation error: {e}")
            return False

    def capture_full_page_screenshot(self, filename: str) -> str:
        """Capture full page screenshot with scrolling"""
        try:
            # Get page dimensions
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Take screenshots while scrolling
            screenshots = []
            current_position = 0
            
            while current_position < total_height:
                # Scroll to position
                self.driver.execute_script(f"window.scrollTo(0, {current_position})")
                time.sleep(1)
                
                # Take screenshot
                screenshot = self.driver.get_screenshot_as_png()
                screenshots.append(Image.open(io.BytesIO(screenshot)))
                
                current_position += viewport_height
            
            # Stitch screenshots together
            if screenshots:
                total_width = screenshots[0].width
                total_height = sum(img.height for img in screenshots)
                
                stitched = Image.new('RGB', (total_width, total_height))
                y_offset = 0
                
                for img in screenshots:
                    stitched.paste(img, (0, y_offset))
                    y_offset += img.height
                
                # Save stitched image
                screenshot_path = self.screenshots_dir / filename
                stitched.save(screenshot_path)
                
                self.logger.info(f"📸 Full page screenshot saved: {screenshot_path}")
                return str(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"❌ Screenshot error: {e}")
            
        # Fallback to regular screenshot
        screenshot_path = self.screenshots_dir / filename
        self.driver.save_screenshot(str(screenshot_path))
        return str(screenshot_path)

    def extract_match_elements(self, site_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract match elements from the page"""
        matches = []
        
        try:
            # Find all match rows
            match_rows = self.driver.find_elements(By.CSS_SELECTOR, site_config['selectors']['match_rows'])
            self.logger.info(f"📊 Found {len(match_rows)} match rows")
            
            for i, row in enumerate(match_rows[:50]):  # Limit to first 50 matches
                try:
                    # Scroll element into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", row)
                    time.sleep(0.5)
                    
                    # Extract basic information
                    match_data = {
                        'element': row,
                        'index': i,
                        'screenshot_region': self.get_element_screenshot_region(row)
                    }
                    
                    # Try to extract text data
                    try:
                        teams = row.find_elements(By.CSS_SELECTOR, site_config['selectors']['team_names'])
                        if len(teams) >= 2:
                            match_data['home_team'] = teams[0].text.strip()
                            match_data['away_team'] = teams[1].text.strip()
                    except:
                        pass
                    
                    try:
                        scores = row.find_elements(By.CSS_SELECTOR, site_config['selectors']['scores'])
                        if scores:
                            match_data['score_text'] = scores[0].text.strip()
                    except:
                        pass
                    
                    try:
                        dates = row.find_elements(By.CSS_SELECTOR, site_config['selectors']['dates'])
                        if dates:
                            match_data['date_text'] = dates[0].text.strip()
                    except:
                        pass
                    
                    matches.append(match_data)
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Error extracting match {i}: {e}")
                    continue
            
            return matches
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting match elements: {e}")
            return []

    def get_element_screenshot_region(self, element) -> Dict[str, int]:
        """Get screenshot region coordinates for an element"""
        try:
            location = element.location
            size = element.size
            
            return {
                'x': location['x'],
                'y': location['y'],
                'width': size['width'],
                'height': size['height']
            }
        except:
            return {'x': 0, 'y': 0, 'width': 0, 'height': 0}

    def process_image_for_ocr(self, image_path: str) -> str:
        """Process image to improve OCR accuracy"""
        try:
            # Load image
            img = cv2.imread(image_path)
            
            if self.config['image_processing']['enhance_contrast']:
                # Enhance contrast
                lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                l = clahe.apply(l)
                img = cv2.merge([l, a, b])
                img = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)
            
            if self.config['image_processing']['denoise']:
                # Denoise
                img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
            
            if self.config['image_processing']['sharpen']:
                # Sharpen
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                img = cv2.filter2D(img, -1, kernel)
            
            if self.config['image_processing']['threshold']:
                # Convert to grayscale and threshold
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Save processed image
            processed_path = self.processed_dir / f"processed_{Path(image_path).name}"
            cv2.imwrite(str(processed_path), img)
            
            return str(processed_path)
            
        except Exception as e:
            self.logger.error(f"❌ Image processing error: {e}")
            return image_path

    def extract_text_with_ocr(self, image_path: str, region: Optional[Dict[str, int]] = None) -> str:
        """Extract text from image using OCR"""
        try:
            if self.config['ocr_engine'] == 'easyocr':
                # Use EasyOCR
                if region:
                    # Crop image to region
                    img = cv2.imread(image_path)
                    cropped = img[region['y']:region['y']+region['height'], 
                                region['x']:region['x']+region['width']]
                    
                    # Save cropped image
                    cropped_path = self.processed_dir / f"cropped_{int(time.time())}.png"
                    cv2.imwrite(str(cropped_path), cropped)
                    
                    # Process for OCR
                    processed_path = self.process_image_for_ocr(str(cropped_path))
                    
                    # Extract text
                    results = self.ocr_reader.readtext(processed_path)
                    text = ' '.join([result[1] for result in results if result[2] > 0.5])
                else:
                    # Process full image
                    processed_path = self.process_image_for_ocr(image_path)
                    results = self.ocr_reader.readtext(processed_path)
                    text = ' '.join([result[1] for result in results if result[2] > 0.5])
            
            else:
                # Use Tesseract
                if region:
                    img = Image.open(image_path)
                    cropped = img.crop((region['x'], region['y'], 
                                     region['x']+region['width'], 
                                     region['y']+region['height']))
                    text = pytesseract.image_to_string(cropped)
                else:
                    processed_path = self.process_image_for_ocr(image_path)
                    text = pytesseract.image_to_string(processed_path)
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"❌ OCR error: {e}")
            return ""

    def parse_match_result(self, match_data: Dict[str, Any], ocr_text: str) -> Optional[MatchResult]:
        """Parse match result from extracted data and OCR text"""
        try:
            # Initialize result
            result = MatchResult(
                match_id=f"match_{int(time.time())}_{match_data['index']}",
                date="",
                home_team="",
                away_team="",
                home_score=0,
                away_score=0,
                competition="",
                betting_odds={},
                result_type="",
                confidence_score=0.0
            )
            
            # Extract team names
            if 'home_team' in match_data and 'away_team' in match_data:
                result.home_team = match_data['home_team']
                result.away_team = match_data['away_team']
                result.confidence_score += 0.3
            else:
                # Try to extract from OCR
                teams = self.extract_teams_from_text(ocr_text)
                if teams:
                    result.home_team, result.away_team = teams
                    result.confidence_score += 0.2
            
            # Extract scores
            if 'score_text' in match_data:
                scores = self.extract_scores_from_text(match_data['score_text'])
                if scores:
                    result.home_score, result.away_score = scores
                    result.confidence_score += 0.3
            else:
                # Try to extract from OCR
                scores = self.extract_scores_from_text(ocr_text)
                if scores:
                    result.home_score, result.away_score = scores
                    result.confidence_score += 0.2
            
            # Extract date
            if 'date_text' in match_data:
                result.date = self.parse_date(match_data['date_text'])
                result.confidence_score += 0.2
            else:
                result.date = self.parse_date(ocr_text)
                result.confidence_score += 0.1
            
            # Determine result type
            if result.home_score > result.away_score:
                result.result_type = 'home_win'
            elif result.away_score > result.home_score:
                result.result_type = 'away_win'
            else:
                result.result_type = 'draw'
            
            # Only return if we have minimum required data
            if result.home_team and result.away_team and result.confidence_score > 0.3:
                return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing match result: {e}")
            return None

    def extract_teams_from_text(self, text: str) -> Optional[Tuple[str, str]]:
        """Extract team names from text using patterns"""
        import re
        
        # Common patterns for team vs team
        patterns = [
            r'([A-Za-z\s]+)\s+vs?\s+([A-Za-z\s]+)',
            r'([A-Za-z\s]+)\s+-\s+([A-Za-z\s]+)',
            r'([A-Za-z\s]+)\s+v\s+([A-Za-z\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                home_team = match.group(1).strip()
                away_team = match.group(2).strip()
                if len(home_team) > 2 and len(away_team) > 2:
                    return (home_team, away_team)
        
        return None

    def extract_scores_from_text(self, text: str) -> Optional[Tuple[int, int]]:
        """Extract scores from text using patterns"""
        import re
        
        # Common score patterns
        patterns = [
            r'(\d+)\s*-\s*(\d+)',
            r'(\d+)\s*:\s*(\d+)',
            r'(\d+)\s+(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    home_score = int(match.group(1))
                    away_score = int(match.group(2))
                    return (home_score, away_score)
                except ValueError:
                    continue
        
        return None

    def parse_date(self, text: str) -> str:
        """Parse date from text"""
        import re
        from dateutil import parser
        
        # Try to find date patterns
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'\d{4}-\d{1,2}-\d{1,2}',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    parsed_date = parser.parse(match.group())
                    return parsed_date.strftime('%Y-%m-%d')
                except:
                    continue
        
        # Default to today if no date found
        return datetime.now().strftime('%Y-%m-%d')

    def save_match_result(self, result: MatchResult, site_name: str):
        """Save match result to database"""
        try:
            conn = sqlite3.connect('betting_history.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO match_results 
                (match_id, date, home_team, away_team, home_score, away_score, 
                 competition, betting_odds, result_type, screenshot_path, 
                 confidence_score, site_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.match_id, result.date, result.home_team, result.away_team,
                result.home_score, result.away_score, result.competition,
                json.dumps(result.betting_odds), result.result_type,
                result.screenshot_path, result.confidence_score, site_name
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"💾 Saved match result: {result.home_team} vs {result.away_team}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving match result: {e}")

    def extract_betting_history(self, site_name: str, credentials: Optional[Dict[str, str]] = None) -> List[MatchResult]:
        """Main method to extract betting history from a site"""
        session_id = f"session_{int(time.time())}"
        results = []
        
        try:
            # Get site configuration
            site_config = self.config['betting_sites'].get(site_name)
            if not site_config:
                self.logger.error(f"❌ Site configuration not found: {site_name}")
                return results
            
            self.logger.info(f"🎯 Starting extraction from {site_config['name']}")
            
            # Setup driver
            self.driver = self.setup_driver(headless=False)
            
            # Login if required
            if site_config.get('login_required') and credentials:
                if not self.login_to_site(site_config, credentials):
                    return results
            
            # Navigate to history section
            if not self.navigate_to_history_section(site_config):
                return results
            
            # Take full page screenshot
            screenshot_path = self.capture_full_page_screenshot(f"{site_name}_history_{int(time.time())}.png")
            
            # Extract match elements
            matches = self.extract_match_elements(site_config)
            self.logger.info(f"📊 Processing {len(matches)} matches")
            
            # Process each match
            for match_data in matches:
                try:
                    # Extract text using OCR from the match region
                    ocr_text = ""
                    if match_data.get('screenshot_region'):
                        ocr_text = self.extract_text_with_ocr(screenshot_path, match_data['screenshot_region'])
                    
                    # Parse match result
                    result = self.parse_match_result(match_data, ocr_text)
                    
                    if result:
                        result.screenshot_path = screenshot_path
                        self.save_match_result(result, site_name)
                        results.append(result)
                        
                        self.logger.info(f"✅ Extracted: {result.home_team} {result.home_score}-{result.away_score} {result.away_team}")
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Error processing match: {e}")
                    continue
            
            self.logger.info(f"🎉 Extraction completed: {len(results)} matches extracted")
            
        except Exception as e:
            self.logger.error(f"❌ Extraction failed: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
        
        return results

def create_sample_config():
    """Create sample configuration file"""
    config = {
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
            }
        }
    }
    
    with open('betting_extractor_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Sample configuration created: betting_extractor_config.json")

def main():
    """Main function for testing"""
    print("🎯 Betting Visual History Extractor")
    print("=" * 50)
    
    # Create sample config if not exists
    if not os.path.exists('betting_extractor_config.json'):
        create_sample_config()
    
    # Initialize extractor
    extractor = BettingVisualHistoryExtractor()
    
    # Example usage
    print("🚀 Starting extraction from FlashScore...")
    results = extractor.extract_betting_history('flashscore')
    
    print(f"\n📊 Extraction Results:")
    print(f"  Total matches extracted: {len(results)}")
    
    for result in results[:5]:  # Show first 5 results
        print(f"  {result.home_team} {result.home_score}-{result.away_score} {result.away_team} ({result.date})")
    
    print(f"\n💾 Results saved to database: betting_history.db")
    print(f"📸 Screenshots saved to: betting_screenshots/")

if __name__ == "__main__":
    main()