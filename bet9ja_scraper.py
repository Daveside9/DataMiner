#!/usr/bin/env python3
"""
Bet9ja Specialized Scraper
Optimized for Nigerian betting site Bet9ja
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time

# Try to import Selenium (optional)
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

class Bet9jaScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Bet9ja specific URLs
        self.bet9ja_urls = {
            'live_betting': 'https://sports.bet9ja.com/mobile/liveBetting',
            'football': 'https://sports.bet9ja.com/mobile/sport/1',
            'live_scores': 'https://sports.bet9ja.com/mobile/live',
            'desktop': 'https://sports.bet9ja.com/sport/1'
        }
        
        # Nigerian and international team patterns
        self.nigerian_teams = [
            'Rivers United', 'Enyimba', 'Kano Pillars', 'Plateau United', 'Akwa United',
            'Lobi Stars', 'Heartland', 'Kwara United', 'Sunshine Stars', 'Remo Stars',
            'Shooting Stars', 'Bendel Insurance', 'Wikki Tourist', 'Nasarawa United',
            'Abia Warriors', 'Dakkada', 'Adamawa United', 'FC IfeanyiUbah'
        ]
    
    def scrape_bet9ja_live(self, specific_teams=None):
        """Scrape live matches from Bet9ja"""
        print("🇳🇬 Scraping Bet9ja for live matches...")
        
        matches = []
        
        # Try multiple Bet9ja URLs
        for url_name, url in self.bet9ja_urls.items():
            print(f"🔍 Trying {url_name}: {url}")
            
            try:
                if SELENIUM_AVAILABLE:
                    url_matches = self.scrape_with_selenium(url, specific_teams)
                else:
                    url_matches = self.scrape_basic(url, specific_teams)
                
                if url_matches:
                    matches.extend(url_matches)
                    print(f"✅ Found {len(url_matches)} matches from {url_name}")
                else:
                    print(f"❌ No matches from {url_name}")
            
            except Exception as e:
                print(f"❌ Error with {url_name}: {e}")
                continue
        
        return matches
    
    def scrape_with_selenium(self, url, specific_teams=None):
        """Enhanced scraping with Selenium for Bet9ja"""
        print(f"🌐 Using Selenium for Bet9ja: {url}")
        
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={self.headers['User-Agent']}")
            
            # Initialize driver
            driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            driver.get(url)
            
            # Wait for page to load
            print("⏳ Waiting for Bet9ja to load...")
            time.sleep(8)  # Bet9ja might need more time
            
            # Wait for dynamic content
            try:
                WebDriverWait(driver, 15).until(
                    lambda d: len(d.find_elements(By.TAG_NAME, "body")) > 0
                )
            except:
                pass
            
            # Get page source after JavaScript execution
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            print(f"📄 Bet9ja page loaded: {len(page_source)} characters")
            
            matches = []
            
            # Method 1: Look for Bet9ja specific selectors
            matches.extend(self.extract_bet9ja_matches(soup, driver, specific_teams))
            
            # Method 2: General pattern matching
            if not matches:
                matches.extend(self.extract_general_patterns(soup.get_text(), specific_teams))
            
            driver.quit()
            
            return matches
                
        except Exception as e:
            print(f"❌ Selenium error for Bet9ja: {e}")
            try:
                driver.quit()
            except:
                pass
            return self.scrape_basic(url, specific_teams)
    
    def extract_bet9ja_matches(self, soup, driver, specific_teams=None):
        """Extract matches using Bet9ja-specific selectors"""
        matches = []
        
        try:
            # Bet9ja specific selectors (common patterns)
            bet9ja_selectors = [
                '.match-row', '.game-row', '.event-row',
                '.live-match', '.live-game', '.live-event',
                '[class*="match"]', '[class*="game"]', '[class*="event"]',
                '[class*="live"]', '[class*="score"]'
            ]
            
            match_containers = []
            for selector in bet9ja_selectors:
                containers = soup.select(selector)
                match_containers.extend(containers)
            
            print(f"📦 Found {len(match_containers)} potential match containers")
            
            # Look for live indicators
            live_indicators = ['LIVE', 'Live', "'", 'min', 'HT', 'FT', '1H', '2H']
            
            for container in match_containers[:50]:  # Limit to first 50
                try:
                    container_text = container.get_text(strip=True)
                    
                    # Check if it contains live indicators
                    has_live = any(indicator in container_text for indicator in live_indicators)
                    
                    if has_live or len(container_text) > 20:
                        # Look for team names and scores
                        lines = [line.strip() for line in container_text.split('\n') if line.strip()]
                        
                        # Try to extract match data
                        match_data = self.parse_bet9ja_container(lines, specific_teams)
                        if match_data:
                            matches.append(match_data)
                            print(f"🎯 Bet9ja match: {match_data['home_team']} {match_data['home_score']}-{match_data['away_score']} {match_data['away_team']}")
                
                except Exception as e:
                    continue
            
            # Method 2: Direct element search
            if not matches:
                print("🔍 Trying direct element search...")
                all_elements = driver.find_elements(By.XPATH, "//*[string-length(text()) > 10 and string-length(text()) < 100]")
                
                for elem in all_elements[:100]:  # Check first 100 elements
                    try:
                        text = elem.text.strip()
                        if any(indicator in text for indicator in live_indicators):
                            lines = [line.strip() for line in text.split('\n') if line.strip()]
                            match_data = self.parse_bet9ja_container(lines, specific_teams)
                            if match_data:
                                matches.append(match_data)
                                print(f"🎯 Direct element: {match_data['home_team']} {match_data['home_score']}-{match_data['away_score']} {match_data['away_team']}")
                    
                    except Exception as e:
                        continue
        
        except Exception as e:
            print(f"❌ Bet9ja extraction error: {e}")
        
        return matches
    
    def parse_bet9ja_container(self, lines, specific_teams=None):
        """Parse a Bet9ja match container"""
        try:
            # Look for score patterns in the lines
            scores = []
            teams = []
            
            for line in lines:
                # Check for score patterns
                score_match = re.search(r'(\d+)\s*[-–:]\s*(\d+)', line)
                if score_match:
                    home_score = int(score_match.group(1))
                    away_score = int(score_match.group(2))
                    if 0 <= home_score <= 20 and 0 <= away_score <= 20:
                        scores.append((home_score, away_score))
                
                # Check for team names
                if (len(line) > 3 and len(line) < 30 and 
                    not line.isdigit() and 
                    not re.match(r'^\d+[-–:]\d+$', line) and
                    line not in ['LIVE', 'HT', 'FT', 'min', "'", '+', '1H', '2H']):
                    
                    # Check if it's a known team or looks like a team name
                    if (any(team.lower() in line.lower() for team in self.nigerian_teams) or
                        re.match(r'^[A-Z][a-zA-Z\s]+$', line)):
                        teams.append(line)
            
            # Try to match teams with scores
            if scores and len(teams) >= 2:
                home_score, away_score = scores[0]
                home_team = teams[0]
                away_team = teams[1]
                
                # Apply team filter
                if specific_teams:
                    team_match = False
                    for target_team in specific_teams:
                        if (target_team.lower() in home_team.lower() or 
                            target_team.lower() in away_team.lower()):
                            team_match = True
                            break
                    
                    if not team_match:
                        return None
                
                return {
                    'match_id': f"{home_team.replace(' ', '_')}_{away_team.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': home_score,
                    'away_score': away_score,
                    'total_goals': home_score + away_score,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'BET9JA_SCRAPER',
                    'original_score': f"{home_score}-{away_score}"
                }
        
        except Exception as e:
            pass
        
        return None
    
    def extract_general_patterns(self, page_text, specific_teams=None):
        """Extract matches using general patterns"""
        matches = []
        
        try:
            # Nigerian team patterns
            nigerian_patterns = [
                r'(Rivers United|Enyimba|Kano Pillars|Plateau United|Akwa United)\s+(\d+)\s*[-–:]\s*(\d+)\s+(Rivers United|Enyimba|Kano Pillars|Plateau United|Akwa United)',
                r'([A-Z][a-zA-Z\s]+?)\s+(\d+)\s*[-–:]\s*(\d+)\s+([A-Z][a-zA-Z\s]+?)(?=\s*(?:LIVE|HT|FT|min))',
            ]
            
            for pattern in nigerian_patterns:
                pattern_matches = re.finditer(pattern, page_text, re.IGNORECASE)
                for match in pattern_matches:
                    try:
                        if len(match.groups()) == 4:
                            home_team = match.group(1).strip()
                            home_score = int(match.group(2))
                            away_score = int(match.group(3))
                            away_team = match.group(4).strip()
                            
                            if (0 <= home_score <= 20 and 0 <= away_score <= 20 and
                                home_team != away_team and len(home_team) > 2 and len(away_team) > 2):
                                
                                # Apply team filter
                                if specific_teams:
                                    team_match = False
                                    for target_team in specific_teams:
                                        if (target_team.lower() in home_team.lower() or 
                                            target_team.lower() in away_team.lower()):
                                            team_match = True
                                            break
                                    
                                    if not team_match:
                                        continue
                                
                                match_data = {
                                    'match_id': f"{home_team.replace(' ', '_')}_{away_team.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                                    'home_team': home_team,
                                    'away_team': away_team,
                                    'home_score': home_score,
                                    'away_score': away_score,
                                    'total_goals': home_score + away_score,
                                    'timestamp': datetime.now().isoformat(),
                                    'source': 'BET9JA_PATTERN',
                                    'original_score': f"{home_score}-{away_score}"
                                }
                                
                                matches.append(match_data)
                                print(f"🎯 Nigerian pattern: {home_team} {home_score}-{away_score} {away_team}")
                    
                    except (ValueError, IndexError):
                        continue
        
        except Exception as e:
            print(f"❌ Pattern extraction error: {e}")
        
        return matches
    
    def scrape_basic(self, url, specific_teams=None):
        """Basic scraping without Selenium"""
        print(f"📄 Basic scraping for Bet9ja: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            
            print(f"📄 Basic HTML: {len(text)} characters")
            
            # Try general pattern matching
            matches = self.extract_general_patterns(text, specific_teams)
            
            return matches
            
        except Exception as e:
            print(f"❌ Basic scraping error: {e}")
            return []

def test_bet9ja_scraper():
    """Test the Bet9ja scraper"""
    print("🇳🇬 Testing Bet9ja Scraper")
    print("=" * 50)
    
    scraper = Bet9jaScraper()
    
    # Test without team filter
    print("🔍 Testing all matches...")
    matches = scraper.scrape_bet9ja_live()
    
    if matches:
        print(f"✅ Found {len(matches)} matches!")
        for i, match in enumerate(matches[:5], 1):
            print(f"   {i}. {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
            print(f"      Source: {match['source']}")
    else:
        print("❌ No matches found")
    
    # Test with Nigerian teams
    print(f"\n🇳🇬 Testing Nigerian teams...")
    nigerian_teams = ['Rivers United', 'Enyimba', 'Kano Pillars', 'Arsenal', 'Chelsea', 'Liverpool']
    matches = scraper.scrape_bet9ja_live(nigerian_teams)
    
    if matches:
        print(f"✅ Found {len(matches)} matches for Nigerian/Popular teams!")
        for match in matches:
            print(f"   ⚽ {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
    else:
        print("❌ No matches found for specified teams")
    
    return len(matches) > 0 if matches else False

if __name__ == "__main__":
    test_bet9ja_scraper()