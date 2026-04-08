#!/usr/bin/env python3
"""
Enhanced Real-Time Scraper with Selenium Support
Handles JavaScript-rendered content and better pattern detection
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time
import json

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

class EnhancedScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Site-specific selectors for better accuracy
        self.site_selectors = {
            'livescore.com': {
                'match_containers': ['.match', '.fixture', '[data-testid*="match"]', '.event'],
                'team_selectors': ['.team-name', '.participant', '.competitor', '.home', '.away'],
                'score_selectors': ['.score', '.result', '.goals', '[data-testid*="score"]'],
                'live_indicators': ['LIVE', "'", 'min', '+']
            },
            'flashscore.com': {
                'match_containers': ['.event__match', '.match', '.fixture'],
                'team_selectors': ['.event__participant', '.team'],
                'score_selectors': ['.event__score', '.score'],
                'live_indicators': ['LIVE', "'"]
            },
            'bbc.com': {
                'match_containers': ['.fixture', '.match-summary', '.sp-c-fixture'],
                'team_selectors': ['.team-name', '.sp-c-fixture__team-name'],
                'score_selectors': ['.score', '.sp-c-fixture__number'],
                'live_indicators': ['LIVE', 'HT', 'FT']
            }
        }
    
    def scrape_with_selenium(self, url, specific_teams=None):
        """Enhanced scraping with Selenium for JavaScript content"""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium not available - falling back to basic scraping")
            return self.scrape_basic(url, specific_teams)
        
        print(f"🌐 Using Selenium to scrape: {url}")
        
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
            print("⏳ Waiting for page to load...")
            time.sleep(5)
            
            # Wait for dynamic content
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: len(d.find_elements(By.TAG_NAME, "body")) > 0
                )
            except:
                pass
            
            # Get page source after JavaScript execution
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            print(f"📄 Page loaded: {len(page_source)} characters")
            
            # Detect site type for specific selectors
            site_type = self.detect_site_type(url)
            selectors = self.site_selectors.get(site_type, self.site_selectors['livescore.com'])
            
            matches = []
            
            # Method 1: Use site-specific selectors
            print(f"🎯 Using {site_type} selectors...")
            matches.extend(self.extract_matches_with_selectors(soup, selectors, specific_teams))
            
            # Method 2: Fallback to aggressive pattern matching
            if not matches:
                print("🔄 Fallback to pattern matching...")
                matches.extend(self.extract_matches_with_patterns(soup.get_text(), specific_teams))
            
            # Method 3: Direct element search with Selenium
            if not matches:
                print("🔍 Direct element search...")
                matches.extend(self.selenium_element_search(driver, specific_teams))
            
            driver.quit()
            
            if matches:
                print(f"✅ Found {len(matches)} matches with Selenium")
                return matches
            else:
                print("❌ No matches found with Selenium")
                return []
                
        except Exception as e:
            print(f"❌ Selenium error: {e}")
            try:
                driver.quit()
            except:
                pass
            return self.scrape_basic(url, specific_teams)
    
    def selenium_element_search(self, driver, specific_teams=None):
        """Direct element search using Selenium"""
        matches = []
        
        try:
            # Method 1: Look for multi-line text patterns like "Team1\nTeam2\n5\n0"
            all_elements = driver.find_elements(By.XPATH, "//*[string-length(text()) > 10 and string-length(text()) < 200]")
            
            for elem in all_elements:
                try:
                    text = elem.text.strip()
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    
                    # Look for pattern: Team1, Team2, Score1, Score2
                    if len(lines) >= 4:
                        # Check if last two lines are numbers (scores)
                        try:
                            score1 = int(lines[-2])
                            score2 = int(lines[-1])
                            
                            # Valid football scores
                            if 0 <= score1 <= 20 and 0 <= score2 <= 20:
                                # Get team names (usually the first two non-numeric lines)
                                team_lines = []
                                for line in lines[:-2]:  # Exclude the score lines
                                    if (not line.isdigit() and 
                                        line not in ['LIVE', 'HT', 'FT', "'", '+', 'min'] and
                                        len(line) > 2 and len(line) < 30):
                                        team_lines.append(line)
                                
                                if len(team_lines) >= 2:
                                    home_team = team_lines[0]
                                    away_team = team_lines[1]
                                    
                                    match_data = {
                                        'match_id': f"{home_team.replace(' ', '_')}_{away_team.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                                        'home_team': home_team,
                                        'away_team': away_team,
                                        'home_score': score1,
                                        'away_score': score2,
                                        'total_goals': score1 + score2,
                                        'timestamp': datetime.now().isoformat(),
                                        'source': 'SELENIUM_MULTILINE',
                                        'original_score': f"{score1}-{score2}",
                                        'raw_text': text
                                    }
                                    
                                    # Apply team filter
                                    if self.matches_team_filter(match_data, specific_teams):
                                        matches.append(match_data)
                                        print(f"🎯 Selenium multiline: {home_team} {score1}-{score2} {away_team}")
                        
                        except (ValueError, IndexError):
                            continue
                
                except Exception as e:
                    continue
            
            # Method 2: Look for traditional score patterns
            score_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '-') and string-length(text()) < 10]")
            
            for elem in score_elements:
                try:
                    text = elem.text.strip()
                    if re.match(r'^\d+\s*-\s*\d+$', text):
                        # Found a score, now find associated teams
                        parent = elem.find_element(By.XPATH, "./..")
                        grandparent = parent.find_element(By.XPATH, "./..")
                        
                        # Look for team names in parent elements
                        team_elements = grandparent.find_elements(By.XPATH, ".//*[string-length(text()) > 3 and string-length(text()) < 30]")
                        
                        teams = []
                        for team_elem in team_elements:
                            team_text = team_elem.text.strip()
                            if (team_text and 
                                not re.match(r'^\d+$', team_text) and 
                                team_text not in ['LIVE', 'HT', 'FT', '-', "'", '+', 'min'] and
                                len(team_text) > 2):
                                teams.append(team_text)
                        
                        if len(teams) >= 2:
                            home_score, away_score = map(int, text.split('-'))
                            
                            match_data = {
                                'match_id': f"{teams[0].replace(' ', '_')}_{teams[1].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                                'home_team': teams[0],
                                'away_team': teams[1],
                                'home_score': home_score,
                                'away_score': away_score,
                                'total_goals': home_score + away_score,
                                'timestamp': datetime.now().isoformat(),
                                'source': 'SELENIUM_DIRECT',
                                'original_score': text
                            }
                            
                            # Apply team filter
                            if self.matches_team_filter(match_data, specific_teams):
                                matches.append(match_data)
                                print(f"🎯 Selenium direct: {teams[0]} {text} {teams[1]}")
                
                except Exception as e:
                    continue
            
            # Method 3: Look for space-separated scores in context
            page_text = driver.page_source
            soup = BeautifulSoup(page_text, 'html.parser')
            
            # Find patterns like "Team1 Team2 5 0" in the full text
            text_content = soup.get_text()
            
            # Look for team-score patterns
            team_score_pattern = r'([A-Z][a-zA-Z\s]+?)\s+([A-Z][a-zA-Z\s]+?)\s+(\d+)\s+(\d+)'
            matches_found = re.finditer(team_score_pattern, text_content)
            
            for match in matches_found:
                try:
                    home_team = match.group(1).strip()
                    away_team = match.group(2).strip()
                    home_score = int(match.group(3))
                    away_score = int(match.group(4))
                    
                    # Validate
                    if (0 <= home_score <= 20 and 0 <= away_score <= 20 and
                        len(home_team) > 2 and len(away_team) > 2 and
                        home_team != away_team):
                        
                        match_data = {
                            'match_id': f"{home_team.replace(' ', '_')}_{away_team.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                            'home_team': home_team,
                            'away_team': away_team,
                            'home_score': home_score,
                            'away_score': away_score,
                            'total_goals': home_score + away_score,
                            'timestamp': datetime.now().isoformat(),
                            'source': 'SELENIUM_PATTERN',
                            'original_score': f"{home_score}-{away_score}"
                        }
                        
                        # Apply team filter
                        if self.matches_team_filter(match_data, specific_teams):
                            matches.append(match_data)
                            print(f"🎯 Selenium pattern: {home_team} {home_score}-{away_score} {away_team}")
                
                except (ValueError, IndexError):
                    continue
        
        except Exception as e:
            print(f"❌ Selenium element search error: {e}")
        
        return matches
    
    def detect_site_type(self, url):
        """Detect which site we're scraping for specific selectors"""
        if 'livescore.com' in url:
            return 'livescore.com'
        elif 'flashscore.com' in url:
            return 'flashscore.com'
        elif 'bbc.com' in url:
            return 'bbc.com'
        else:
            return 'livescore.com'  # Default
    
    def extract_matches_with_selectors(self, soup, selectors, specific_teams=None):
        """Extract matches using site-specific CSS selectors"""
        matches = []
        
        try:
            # Find match containers
            match_containers = []
            for selector in selectors['match_containers']:
                containers = soup.select(selector)
                match_containers.extend(containers)
            
            print(f"📦 Found {len(match_containers)} match containers")
            
            for container in match_containers[:20]:  # Limit to first 20
                try:
                    # Extract teams
                    teams = []
                    for team_selector in selectors['team_selectors']:
                        team_elements = container.select(team_selector)
                        for elem in team_elements:
                            team_text = elem.get_text(strip=True)
                            if team_text and len(team_text) > 2:
                                teams.append(team_text)
                    
                    # Extract scores
                    scores = []
                    for score_selector in selectors['score_selectors']:
                        score_elements = container.select(score_selector)
                        for elem in score_elements:
                            score_text = elem.get_text(strip=True)
                            if re.match(r'^\d+\s*-\s*\d+$', score_text):
                                scores.append(score_text)
                    
                    # Check for live indicators
                    container_text = container.get_text()
                    is_live = any(indicator in container_text for indicator in selectors['live_indicators'])
                    
                    # Create match if we have teams and scores
                    if len(teams) >= 2 and scores:
                        score_parts = scores[0].split('-')
                        if len(score_parts) == 2:
                            home_score = int(score_parts[0].strip())
                            away_score = int(score_parts[1].strip())
                            
                            match_data = {
                                'match_id': f"{teams[0].replace(' ', '_')}_{teams[1].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                                'home_team': teams[0],
                                'away_team': teams[1],
                                'home_score': home_score,
                                'away_score': away_score,
                                'total_goals': home_score + away_score,
                                'timestamp': datetime.now().isoformat(),
                                'source': 'CSS_SELECTORS',
                                'is_live': is_live,
                                'original_score': scores[0]
                            }
                            
                            if self.matches_team_filter(match_data, specific_teams):
                                matches.append(match_data)
                                print(f"🎯 CSS found: {teams[0]} {scores[0]} {teams[1]} {'(LIVE)' if is_live else ''}")
                
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"❌ CSS selector error: {e}")
        
        return matches
    
    def extract_matches_with_patterns(self, page_text, specific_teams=None):
        """Extract matches using pattern matching (fallback method)"""
        matches = []
        
        try:
            # ENHANCED PATTERN MATCHING - Based on actual site formats
            
            # Pattern 1: "Team1Team2ScoreScore" (like Flashscore concatenated format)
            team_score_patterns = [
                # Specific U23 patterns (concatenated format)
                r'([A-Z][a-zA-Z\s]+?U23)([A-Z][a-zA-Z\s]+?U23)(\d)(\d)',  # Japan U23Syria U2350
                r'([A-Z][a-zA-Z\s]+?U23)\s+([A-Z][a-zA-Z\s]+?U23)\s+(\d+)\s*(\d+)',  # With spaces
                
                # General team patterns (with proper spacing)
                r'([A-Z][a-zA-Z\s]{3,20})\s+([A-Z][a-zA-Z\s]{3,20})\s+(\d+)\s+(\d+)',  # Team1 Team2 5 0
                
                # Avoid matching website text by being more specific
                r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(\d+)\s+(\d+)(?=\s*(?:LIVE|HT|FT|min|$))',
            ]
            
            for pattern in team_score_patterns:
                pattern_matches = re.finditer(pattern, page_text, re.IGNORECASE)
                for match in pattern_matches:
                    try:
                        home_team = match.group(1).strip()
                        away_team = match.group(2).strip()
                        
                        # Handle different score formats
                        if len(match.groups()) == 4:
                            # Check if it's concatenated single digits (like "50" for 5-0)
                            if (len(match.group(3)) == 1 and len(match.group(4)) == 1):
                                home_score = int(match.group(3))
                                away_score = int(match.group(4))
                            else:
                                # Regular format
                                home_score = int(match.group(3))
                                away_score = int(match.group(4))
                        else:
                            continue
                        
                        # Validate team names to avoid website text
                        if (0 <= home_score <= 20 and 0 <= away_score <= 20 and
                            len(home_team) > 2 and len(away_team) > 2 and
                            home_team != away_team and
                            self.is_valid_team_name(home_team) and
                            self.is_valid_team_name(away_team) and
                            not any(word in home_team.lower() for word in ['com', 'offers', 'results', 'more', 'than', 'rumors', 'show', 'version', 'betting', 'odds']) and
                            not any(word in away_team.lower() for word in ['com', 'offers', 'results', 'more', 'than', 'rumors', 'show', 'version', 'betting', 'odds'])):
                            
                            match_data = {
                                'match_id': f"{home_team.replace(' ', '_')}_{away_team.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                                'home_team': home_team,
                                'away_team': away_team,
                                'home_score': home_score,
                                'away_score': away_score,
                                'total_goals': home_score + away_score,
                                'timestamp': datetime.now().isoformat(),
                                'source': 'PATTERN_TEAM_SCORE',
                                'original_score': f"{home_score}-{away_score}",
                                'pattern_used': pattern
                            }
                            
                            if self.matches_team_filter(match_data, specific_teams):
                                matches.append(match_data)
                                print(f"🎯 Team-Score pattern: {home_team} {home_score}-{away_score} {away_team}")
                    
                    except (ValueError, IndexError):
                        continue
            
            # Pattern 2: Traditional score patterns with nearby teams
            score_patterns = [
                r'\b(\d+)\s*[-–—]\s*(\d+)\b',
                r'\b(\d+)\s*:\s*(\d+)\b',
                r'\((\d+)\s*[-–]\s*(\d+)\)',
            ]
            
            all_scores = []
            for pattern in score_patterns:
                matches_found = re.finditer(pattern, page_text, re.IGNORECASE)
                for match in matches_found:
                    home_score = int(match.group(1))
                    away_score = int(match.group(2))
                    
                    # Valid football scores and not time patterns
                    if (0 <= home_score <= 20 and 0 <= away_score <= 20 and
                        not (home_score >= 12 and away_score >= 30)):  # Exclude times like 12:30
                        all_scores.append({
                            'home_score': home_score,
                            'away_score': away_score,
                            'original': match.group(0),
                            'position': match.start()
                        })
            
            print(f"🎯 Found {len(all_scores)} potential scores")
            
            # Enhanced team detection
            team_patterns = [
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:FC|CF|AC|SC|United|City|Town|Rovers|Wanderers|Athletic|Hotspur|U23))\b',
                r'\b(?:Arsenal|Chelsea|Liverpool|Manchester\s+(?:City|United)|Tottenham|Barcelona|Real\s+Madrid|Bayern|PSG|Juventus|Milan|Inter|Brighton|Newcastle|Everton|Leeds|Wolves|Crystal\s+Palace)\b',
                r'\b[A-Z]{3,4}\b(?=\s*(?:\d+[-–]\d+|LIVE))',
                r'\b[A-Z][a-z]{3,}\s+[A-Z][a-z]{3,}\b'
            ]
            
            all_teams = []
            for pattern in team_patterns:
                teams_found = re.finditer(pattern, page_text, re.IGNORECASE)
                for match in teams_found:
                    team_name = match.group(0).strip()
                    if self.is_valid_team_name(team_name):
                        all_teams.append({
                            'name': team_name,
                            'position': match.start()
                        })
            
            print(f"⚽ Found {len(all_teams)} potential teams")
            
            # Match scores with nearby teams
            for score in all_scores[:10]:  # Limit processing
                nearby_teams = []
                
                # Find teams within 500 characters of the score
                for team in all_teams:
                    distance = abs(team['position'] - score['position'])
                    if distance < 500:
                        nearby_teams.append((team['name'], distance))
                
                # Sort by distance and take closest teams
                nearby_teams.sort(key=lambda x: x[1])
                
                if len(nearby_teams) >= 2:
                    home_team = nearby_teams[0][0]
                    away_team = nearby_teams[1][0]
                    
                    match_data = {
                        'match_id': f"{home_team.replace(' ', '_')}_{away_team.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_score': score['home_score'],
                        'away_score': score['away_score'],
                        'total_goals': score['home_score'] + score['away_score'],
                        'timestamp': datetime.now().isoformat(),
                        'source': 'PATTERN_MATCHING',
                        'original_score': score['original']
                    }
                    
                    if self.matches_team_filter(match_data, specific_teams):
                        matches.append(match_data)
                        print(f"🎯 Pattern found: {home_team} {score['original']} {away_team}")
        
        except Exception as e:
            print(f"❌ Pattern matching error: {e}")
        
        return matches
    
    def is_valid_team_name(self, name):
        """Check if a string is a valid team name"""
        excluded = {
            'LIVE', 'Score', 'Match', 'Game', 'Today', 'Tomorrow', 'Yesterday',
            'Premier', 'League', 'Championship', 'Division', 'Table', 'News',
            'Home', 'Away', 'Full', 'Time', 'Half', 'Final', 'Result', 'Goals',
            'Cards', 'Corners', 'Fouls', 'Shots', 'Possession', 'Substitutions',
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        }
        
        return (len(name) > 2 and 
                name not in excluded and 
                not name.isdigit() and
                not re.match(r'^\d+[-–]\d+$', name))
    
    def matches_team_filter(self, match_data, specific_teams):
        """Check if match matches team filter"""
        if not specific_teams:
            return True
        
        for target_team in specific_teams:
            if (target_team.lower() in match_data['home_team'].lower() or 
                target_team.lower() in match_data['away_team'].lower()):
                return True
        
        return False
    
    def scrape_basic(self, url, specific_teams=None):
        """Basic scraping without Selenium"""
        print(f"📄 Using basic scraping: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try pattern matching
            matches = self.extract_matches_with_patterns(soup.get_text(), specific_teams)
            
            if matches:
                print(f"✅ Basic scraping found {len(matches)} matches")
            else:
                print("❌ Basic scraping found no matches")
            
            return matches
            
        except Exception as e:
            print(f"❌ Basic scraping error: {e}")
            return []
    
    def scrape_live_scores(self, url, specific_teams=None):
        """Main scraping method - tries Selenium first, falls back to basic"""
        print(f"🚀 Starting enhanced scraping...")
        print(f"🌐 URL: {url}")
        if specific_teams:
            print(f"🎯 Teams: {', '.join(specific_teams)}")
        
        # Try Selenium first for better results
        matches = self.scrape_with_selenium(url, specific_teams)
        
        # If Selenium fails or finds nothing, try basic scraping
        if not matches:
            print("🔄 Trying basic scraping as fallback...")
            matches = self.scrape_basic(url, specific_teams)
        
        return matches

def test_enhanced_scraper():
    """Test the enhanced scraper"""
    scraper = EnhancedScraper()
    
    test_urls = [
        'https://www.livescore.com/en/football/',
        'https://www.flashscore.com/football/',
        'https://www.bbc.com/sport/football/scores-fixtures'
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print('='*60)
        
        matches = scraper.scrape_live_scores(url)
        
        if matches:
            print(f"✅ SUCCESS: Found {len(matches)} matches")
            for match in matches[:3]:
                print(f"   ⚽ {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
        else:
            print("❌ No matches found")

if __name__ == "__main__":
    test_enhanced_scraper()