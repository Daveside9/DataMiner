#!/usr/bin/env python3
"""
Bet9ja History Extractor
Specialized extractor for Bet9ja match history and event details
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import json
from urllib.parse import urlparse, parse_qs

# Try to import Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium not available - using basic scraping only")

class Bet9jaHistoryExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://sports.bet9ja.com/'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def extract_match_history_from_url(self, url):
        """Extract match history from a specific Bet9ja URL"""
        print(f"🔍 Extracting history from: {url}")
        
        try:
            # Parse the URL to understand the match
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.split('/')
            
            # Extract team names from URL
            teams_info = self.parse_bet9ja_url(url)
            print(f"📊 Teams detected: {teams_info}")
            
            if SELENIUM_AVAILABLE:
                return self.extract_with_selenium(url, teams_info)
            else:
                return self.extract_basic(url, teams_info)
                
        except Exception as e:
            print(f"❌ Error extracting from URL: {e}")
            return None
    
    def parse_bet9ja_url(self, url):
        """Parse Bet9ja URL to extract team information"""
        try:
            # Example URL: https://sports.bet9ja.com/mobile/eventdetail/zoomsoccer/premier-zoom/premier-zoom/z.crystalpalace-z.manunited/717892344/VS_1X2
            
            path_parts = url.split('/')
            teams_info = {
                'home_team': None,
                'away_team': None,
                'league': None,
                'event_id': None
            }
            
            # Look for team names in URL
            for part in path_parts:
                if '-' in part and ('.' in part or 'z.' in part):
                    # This might be the teams part
                    team_part = part.replace('z.', '').replace('.', ' ')
                    if '-' in team_part:
                        team_names = team_part.split('-')
                        if len(team_names) >= 2:
                            teams_info['home_team'] = team_names[0].replace('_', ' ').title()
                            teams_info['away_team'] = team_names[1].replace('_', ' ').title()
                
                # Look for event ID (usually a number)
                if part.isdigit() and len(part) > 6:
                    teams_info['event_id'] = part
                
                # Look for league info
                if 'premier' in part.lower() or 'league' in part.lower():
                    teams_info['league'] = part.replace('-', ' ').title()
            
            return teams_info
            
        except Exception as e:
            print(f"❌ URL parsing error: {e}")
            return {'home_team': None, 'away_team': None, 'league': None, 'event_id': None}
    
    def extract_with_selenium(self, url, teams_info):
        """Extract match history using Selenium"""
        print("🌐 Using Selenium for Bet9ja history extraction...")
        
        try:
            # Setup Chrome options for Bet9ja
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={self.headers['User-Agent']}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Initialize driver
            driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Execute script to hide webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Load the page
            driver.get(url)
            print("⏳ Loading Bet9ja page...")
            time.sleep(10)  # Give Bet9ja time to load
            
            # Wait for content to load
            try:
                WebDriverWait(driver, 20).until(
                    lambda d: len(d.find_elements(By.TAG_NAME, "body")) > 0
                )
            except:
                pass
            
            # Get page source
            page_source = driver.page_source
            print(f"📄 Page loaded: {len(page_source)} characters")
            
            # Extract match data
            match_data = self.parse_bet9ja_page(page_source, teams_info, driver)
            
            # Try to find historical data links or sections
            history_data = self.find_historical_data(driver, teams_info)
            
            if history_data:
                match_data['historical_matches'] = history_data
            
            driver.quit()
            
            return match_data
            
        except Exception as e:
            print(f"❌ Selenium extraction error: {e}")
            try:
                driver.quit()
            except:
                pass
            return self.extract_basic(url, teams_info)
    
    def parse_bet9ja_page(self, page_source, teams_info, driver=None):
        """Parse Bet9ja page content for match information"""
        soup = BeautifulSoup(page_source, 'html.parser')
        
        match_data = {
            'source': 'Bet9ja',
            'url': driver.current_url if driver else 'Unknown',
            'extraction_time': datetime.now().isoformat(),
            'teams': teams_info,
            'current_odds': {},
            'match_details': {},
            'live_score': None,
            'is_live': False
        }
        
        try:
            page_text = soup.get_text()
            
            # Enhanced live score detection
            live_score_patterns = [
                # Pattern 1: Standard score format
                r'(\d+)\s*[-–:]\s*(\d+)',
                # Pattern 2: Score with context
                r'Score[:\s]*(\d+)\s*[-–:]\s*(\d+)',
                # Pattern 3: Live score indicators
                r'(\d+)\s*vs\s*(\d+)',
                # Pattern 4: Team names with scores
                rf'{re.escape(teams_info.get("home_team", ""))}\s*(\d+)\s*[-–:]\s*(\d+)\s*{re.escape(teams_info.get("away_team", ""))}',
                # Pattern 5: Reverse team order
                rf'{re.escape(teams_info.get("away_team", ""))}\s*(\d+)\s*[-–:]\s*(\d+)\s*{re.escape(teams_info.get("home_team", ""))}',
            ]
            
            # Check for live indicators first
            live_indicators = ['LIVE', 'Live', "'", 'min', 'HT', 'FT', '1H', '2H', 'HALF TIME', 'FULL TIME']
            match_data['is_live'] = any(indicator in page_text for indicator in live_indicators)
            
            # Try to find scores
            for i, pattern in enumerate(live_score_patterns):
                try:
                    score_matches = re.finditer(pattern, page_text, re.IGNORECASE)
                    for match in score_matches:
                        try:
                            if len(match.groups()) >= 2:
                                score1 = int(match.group(1))
                                score2 = int(match.group(2))
                                
                                # Validate score range
                                if 0 <= score1 <= 20 and 0 <= score2 <= 20:
                                    # For patterns 4 and 5, we know the team order
                                    if i == 3:  # Home team first
                                        home_score, away_score = score1, score2
                                    elif i == 4:  # Away team first, so reverse
                                        home_score, away_score = score2, score1
                                    else:
                                        # For other patterns, assume first score is home
                                        home_score, away_score = score1, score2
                                    
                                    match_data['live_score'] = {
                                        'home': home_score,
                                        'away': away_score,
                                        'total': home_score + away_score,
                                        'pattern_used': i + 1
                                    }
                                    
                                    print(f"⚽ Live score detected: {home_score}-{away_score} (pattern {i+1})")
                                    break
                        except (ValueError, IndexError):
                            continue
                    
                    if match_data['live_score']:
                        break
                except Exception as e:
                    continue
            
            # Extract current odds with better patterns
            odds_patterns = [
                r'(\d+\.\d{2})',  # Decimal odds
                r'(\d+/\d+)',     # Fractional odds
                r'([+-]\d{3,4})'  # American odds
            ]
            
            # Look for odds in various contexts
            odds_contexts = soup.find_all(['span', 'div', 'td'], class_=re.compile(r'odd|price|rate|bet', re.I))
            for elem in odds_contexts:
                elem_text = elem.get_text(strip=True)
                for pattern in odds_patterns:
                    odds_matches = re.findall(pattern, elem_text)
                    for odds_val in odds_matches:
                        try:
                            # Validate decimal odds
                            if '.' in odds_val and 1.0 <= float(odds_val) <= 50.0:
                                parent_text = elem.parent.get_text(strip=True)[:30] if elem.parent else elem_text[:30]
                                match_data['current_odds'][parent_text] = odds_val
                        except ValueError:
                            continue
            
            # Extract match status and time
            status_patterns = [
                r"(\d+)'",  # Minutes played
                r'(HT|FT|LIVE|Live)',  # Match status
                r'(\d{1,2}:\d{2})',  # Time format
            ]
            
            for pattern in status_patterns:
                status_match = re.search(pattern, page_text)
                if status_match:
                    match_data['match_details']['status'] = status_match.group(1)
                    break
            
            # Extract additional match info
            details_keywords = ['kick off', 'start time', 'venue', 'referee', 'league', 'competition']
            for keyword in details_keywords:
                pattern = rf'{keyword}[:\s]*([^\n\r]+)'
                detail_match = re.search(pattern, page_text, re.IGNORECASE)
                if detail_match:
                    match_data['match_details'][keyword] = detail_match.group(1).strip()[:100]
            
            print(f"✅ Extracted: {len(match_data['current_odds'])} odds, live: {match_data['is_live']}, score: {match_data['live_score']}")
            
        except Exception as e:
            print(f"❌ Page parsing error: {e}")
        
        return match_data
    
    def extract_team_stats(self, soup, teams_info):
        """Extract team statistics from the page"""
        stats = {}
        
        try:
            # Look for statistics sections
            stats_sections = soup.find_all(['div', 'section'], class_=re.compile(r'stat|form|history', re.I))
            
            for section in stats_sections:
                section_text = section.get_text()
                
                # Look for win/loss records
                record_pattern = r'(\d+)\s*W\s*(\d+)\s*D\s*(\d+)\s*L'
                record_match = re.search(record_pattern, section_text)
                if record_match:
                    stats['form'] = {
                        'wins': int(record_match.group(1)),
                        'draws': int(record_match.group(2)),
                        'losses': int(record_match.group(3))
                    }
                
                # Look for recent results
                result_patterns = [
                    r'([WDL])\s*([WDL])\s*([WDL])\s*([WDL])\s*([WDL])',
                    r'Last\s*5[:\s]*([WDLWDL\s]+)'
                ]
                
                for pattern in result_patterns:
                    result_match = re.search(pattern, section_text)
                    if result_match:
                        stats['recent_form'] = result_match.group(0)
                        break
        
        except Exception as e:
            print(f"❌ Stats extraction error: {e}")
        
        return stats
    
    def find_historical_data(self, driver, teams_info):
        """Find and extract historical match data"""
        historical_matches = []
        
        try:
            # Look for links to historical data
            history_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'History') or contains(text(), 'Head') or contains(text(), 'Previous')]")
            
            if history_links:
                print(f"🔍 Found {len(history_links)} history links")
                
                # Click on the first history link
                try:
                    history_links[0].click()
                    time.sleep(5)
                    
                    # Extract historical matches
                    page_source = driver.page_source
                    historical_matches = self.parse_historical_matches(page_source, teams_info)
                    
                except Exception as e:
                    print(f"❌ Error clicking history link: {e}")
            
            # Alternative: Look for historical data in current page
            if not historical_matches:
                historical_matches = self.parse_historical_matches(driver.page_source, teams_info)
        
        except Exception as e:
            print(f"❌ Historical data extraction error: {e}")
        
        return historical_matches
    
    def parse_historical_matches(self, page_source, teams_info):
        """Parse historical matches from page content"""
        matches = []
        
        try:
            soup = BeautifulSoup(page_source, 'html.parser')
            page_text = soup.get_text()
            
            # Look for historical match patterns
            team_names = [teams_info.get('home_team', ''), teams_info.get('away_team', '')]
            team_names = [name for name in team_names if name]
            
            if not team_names:
                return matches
            
            # Pattern for historical matches
            for team in team_names:
                if team:
                    # Look for matches involving this team
                    pattern = rf'{re.escape(team)}.*?(\d+)\s*[-–:]\s*(\d+).*?(\d{{1,2}}/\d{{1,2}}/\d{{2,4}}|\d{{4}}-\d{{2}}-\d{{2}})'
                    
                    historical_matches = re.finditer(pattern, page_text, re.IGNORECASE | re.DOTALL)
                    
                    for match in historical_matches:
                        try:
                            match_text = match.group(0)
                            score1 = int(match.group(1))
                            score2 = int(match.group(2))
                            date_str = match.group(3)
                            
                            if 0 <= score1 <= 20 and 0 <= score2 <= 20:
                                matches.append({
                                    'team': team,
                                    'score1': score1,
                                    'score2': score2,
                                    'date': date_str,
                                    'match_text': match_text[:200]
                                })
                        
                        except (ValueError, IndexError):
                            continue
            
            print(f"📊 Found {len(matches)} historical matches")
        
        except Exception as e:
            print(f"❌ Historical parsing error: {e}")
        
        return matches[:20]  # Limit to 20 most recent
    
    def extract_basic(self, url, teams_info):
        """Basic extraction without Selenium"""
        print("📄 Using basic extraction for Bet9ja...")
        
        try:
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code}")
                return None
            
            match_data = self.parse_bet9ja_page(response.text, teams_info)
            
            return match_data
            
        except Exception as e:
            print(f"❌ Basic extraction error: {e}")
            return None

def test_bet9ja_extractor():
    """Test the Bet9ja history extractor"""
    print("🇳🇬 Testing Bet9ja History Extractor")
    print("=" * 60)
    
    extractor = Bet9jaHistoryExtractor()
    
    # Test URL from user
    test_url = "https://sports.bet9ja.com/mobile/eventdetail/zoomsoccer/premier-zoom/premier-zoom/z.crystalpalace-z.manunited/717892344/VS_1X2"
    
    print(f"🔍 Testing URL: {test_url}")
    
    result = extractor.extract_match_history_from_url(test_url)
    
    if result:
        print("✅ Extraction successful!")
        print(f"📊 Teams: {result['teams']}")
        print(f"⚽ Live Score: {result['live_score']}")
        print(f"💰 Odds Found: {len(result['current_odds'])}")
        print(f"📈 Historical Matches: {len(result.get('historical_matches', []))}")
        
        # Display some details
        if result['current_odds']:
            print("\n💰 Current Odds:")
            for market, odds in list(result['current_odds'].items())[:5]:
                print(f"   {market}: {odds}")
        
        if result.get('historical_matches'):
            print("\n📊 Historical Matches:")
            for match in result['historical_matches'][:3]:
                print(f"   {match['team']}: {match['score1']}-{match['score2']} ({match['date']})")
    
    else:
        print("❌ Extraction failed")
    
    return result

if __name__ == "__main__":
    test_bet9ja_extractor()