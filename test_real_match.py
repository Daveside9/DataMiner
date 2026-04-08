#!/usr/bin/env python3
"""
Test Real Match Detection
Focus on finding the actual Japan U23 vs Syria U23 match
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_scraper import EnhancedScraper
import re

def test_flashscore_real_match():
    """Test Flashscore for the real match we know exists"""
    print("🎯 Testing Flashscore for Japan U23 vs Syria U23...")
    
    scraper = EnhancedScraper()
    
    # Override the pattern matching to be more specific
    def find_real_matches(page_text):
        matches = []
        
        # Look specifically for the pattern we found: "Japan U23Syria U2350"
        specific_patterns = [
            r'Japan U23Syria U23(\d+)(\d+)',  # No spaces: "Japan U23Syria U2350"
            r'Japan U23\s+Syria U23\s+(\d+)\s*(\d+)',  # With spaces
            r'([A-Z][a-zA-Z\s]+?U23)([A-Z][a-zA-Z\s]+?U23)(\d+)(\d+)',  # General no-space pattern
            r'([A-Z][a-zA-Z\s]+?U23)\s+([A-Z][a-zA-Z\s]+?U23)\s+(\d+)\s*(\d+)',  # General with spaces
            r'South Korea U23Iran U23(\d+)(\d+)',
            r'Uzbekistan U23Lebanon U23(\d+)(\d+)',
            r'Qatar U23United Arab Emirates U23(\d+)(\d+)',
        ]
        
        for pattern in specific_patterns:
            pattern_matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in pattern_matches:
                try:
                    if 'Japan U23Syria U23' in match.group(0):
                        home_team = "Japan U23"
                        away_team = "Syria U23"
                        # Handle single or double digit scores
                        score_part = match.group(1) + match.group(2)
                        if len(score_part) == 2:  # "50" -> 5-0
                            home_score = int(score_part[0])
                            away_score = int(score_part[1])
                        else:
                            home_score = int(match.group(1))
                            away_score = int(match.group(2))
                    elif 'Japan U23' in pattern:
                        home_team = "Japan U23"
                        away_team = "Syria U23"
                        home_score = int(match.group(1))
                        away_score = int(match.group(2))
                    elif len(match.groups()) == 4:
                        home_team = match.group(1).strip()
                        away_team = match.group(2).strip()
                        # Handle concatenated scores
                        if len(match.group(3)) == 1 and len(match.group(4)) == 1:
                            home_score = int(match.group(3))
                            away_score = int(match.group(4))
                        else:
                            score_part = match.group(3) + match.group(4)
                            if len(score_part) == 2:
                                home_score = int(score_part[0])
                                away_score = int(score_part[1])
                            else:
                                continue
                    else:
                        continue
                    
                    if 0 <= home_score <= 20 and 0 <= away_score <= 20:
                        match_data = {
                            'home_team': home_team,
                            'away_team': away_team,
                            'home_score': home_score,
                            'away_score': away_score,
                            'total_goals': home_score + away_score,
                            'source': 'REAL_MATCH_DETECTED',
                            'pattern': pattern
                        }
                        matches.append(match_data)
                        print(f"✅ REAL MATCH: {home_team} {home_score}-{away_score} {away_team}")
                
                except (ValueError, IndexError) as e:
                    print(f"❌ Error parsing match: {e}")
                    continue
        
        return matches
    
    # Test with Selenium
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from bs4 import BeautifulSoup
        import time
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        driver.get('https://www.flashscore.com/football/')
        time.sleep(5)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        full_text = soup.get_text()
        
        print(f"📄 Page loaded: {len(full_text)} characters")
        
        # Look for our specific matches
        real_matches = find_real_matches(full_text)
        
        if real_matches:
            print(f"🎉 Found {len(real_matches)} REAL matches!")
            return real_matches
        else:
            print("❌ No real matches found")
            
            # Debug: Show context around known teams
            if "Japan U23" in full_text:
                japan_index = full_text.find("Japan U23")
                context = full_text[japan_index-50:japan_index+150]
                print(f"📝 Context around Japan U23: {context}")
        
        driver.quit()
        return real_matches
        
    except Exception as e:
        print(f"❌ Selenium error: {e}")
        return []

def test_with_real_time_system():
    """Test the real-time system with the enhanced scraper"""
    print("\n🚀 Testing Real-Time System Integration...")
    
    try:
        from real_time_system import RealTimeSportsSystem
        
        system = RealTimeSportsSystem()
        
        # Test the scraping method directly
        matches = system.scrape_live_scores('https://www.flashscore.com/football/')
        
        if matches:
            print(f"✅ Real-time system found {len(matches)} matches!")
            for match in matches[:3]:
                print(f"   ⚽ {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
        else:
            print("❌ Real-time system found no matches")
    
    except Exception as e:
        print(f"❌ Real-time system error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Real Match Detection")
    print("=" * 50)
    
    real_matches = test_flashscore_real_match()
    
    if real_matches:
        print(f"\n✅ SUCCESS: Found {len(real_matches)} real matches!")
        test_with_real_time_system()
    else:
        print("\n❌ No real matches detected")
        print("💡 This might be because:")
        print("   - The match has ended")
        print("   - The website structure changed")
        print("   - Different matches are live now")
    
    print("\n🚀 Test complete!")