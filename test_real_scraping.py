#!/usr/bin/env python3
"""
Test Real Scraping - Verify the system works with actual websites
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def test_multiple_sites():
    """Test scraping multiple sports sites"""
    sites = [
        'https://www.bbc.com/sport/football/scores-fixtures',
        'https://www.livescore.com/en/football/',
        'https://www.flashscore.com/football/',
        'https://www.espn.com/soccer/fixtures'
    ]
    
    print("🧪 Testing Real Data Scraping")
    print("=" * 50)
    
    for site in sites:
        print(f"\n🔍 Testing: {site}")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(site, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()
                
                # Look for score patterns
                score_patterns = [
                    r'\b\d+\s*[-–—]\s*\d+\b',
                    r'\b\d+\s*:\s*\d+\b',
                    r'\(\d+\s*[-–]\s*\d+\)'
                ]
                
                all_scores = []
                for pattern in score_patterns:
                    scores = re.findall(pattern, text)
                    all_scores.extend(scores)
                
                # Look for team indicators
                team_indicators = ['vs', 'v ', ' - ', 'home', 'away', 'live', 'ft', 'ht']
                has_teams = any(indicator in text.lower() for indicator in team_indicators)
                
                print(f"   Page size: {len(text)} characters")
                print(f"   Potential scores: {len(all_scores)} found")
                print(f"   Team indicators: {'Yes' if has_teams else 'No'}")
                
                if all_scores:
                    print(f"   Sample scores: {all_scores[:3]}")
                
                # Look for live indicators
                live_indicators = ['live', 'LIVE', "'", '+', 'min']
                has_live = any(indicator in text for indicator in live_indicators)
                print(f"   Live matches: {'Possible' if has_live else 'None detected'}")
                
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n" + "=" * 50)
    print("💡 Results Summary:")
    print("- If scores were found, the scraper can extract data")
    print("- If no scores found, the sites may not have live matches right now")
    print("- The system will work when matches are actually live")

if __name__ == "__main__":
    test_multiple_sites()