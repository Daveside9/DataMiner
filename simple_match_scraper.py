#!/usr/bin/env python3
"""
Simple Match Scraper - Basic working version for testing
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def simple_scrape_test():
    """Test basic scraping functionality"""
    print("🧪 Testing Simple Match Scraper")
    print("=" * 40)
    
    # Test with a simple, reliable website
    test_urls = [
        "https://www.bbc.com/sport/football/scores-fixtures",
        "https://www.espn.com/soccer/fixtures",
        "https://quotes.toscrape.com"  # Fallback test site
    ]
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find any text elements that might contain team names
                text_elements = soup.find_all(['div', 'span', 'p'], limit=20)
                
                print(f"✅ Successfully connected!")
                print(f"   Status: {response.status_code}")
                print(f"   Content length: {len(response.content)} bytes")
                print(f"   Found {len(text_elements)} text elements")
                
                # Show first few text elements
                for i, elem in enumerate(text_elements[:5]):
                    text = elem.get_text(strip=True)
                    if text and len(text) > 3:
                        print(f"   Sample text {i+1}: {text[:50]}...")
                
                return True
                
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    return False

def scrape_with_basic_selectors(url, team_name=""):
    """Scrape with very basic, common selectors"""
    print(f"\n🎯 Scraping {url} for team: {team_name}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple common selectors
        selectors_to_try = {
            'teams': [
                '.team', '.team-name', '.home', '.away', 
                '.participant', '.competitor', '.club',
                '[class*="team"]', '[class*="home"]', '[class*="away"]'
            ],
            'dates': [
                '.date', '.time', '.match-date', '.fixture-date',
                '[class*="date"]', '[class*="time"]'
            ],
            'matches': [
                '.match', '.fixture', '.game', '.event',
                '[class*="match"]', '[class*="fixture"]'
            ]
        }
        
        results = {}
        
        for data_type, selectors in selectors_to_try.items():
            found_elements = []
            
            for selector in selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        for elem in elements[:10]:  # Limit to first 10
                            text = elem.get_text(strip=True)
                            if text and len(text) > 1:
                                found_elements.append(text)
                        
                        if found_elements:
                            print(f"✅ Found {len(found_elements)} {data_type} with selector: {selector}")
                            break
                except:
                    continue
            
            results[data_type] = found_elements[:20]  # Limit results
        
        # Filter for team if specified
        if team_name and results.get('teams'):
            team_lower = team_name.lower()
            filtered_teams = [
                team for team in results['teams'] 
                if team_lower in team.lower() or any(word in team.lower() for word in team_lower.split())
            ]
            
            if filtered_teams:
                print(f"🎯 Found {len(filtered_teams)} matches for '{team_name}':")
                for team in filtered_teams[:5]:
                    print(f"   - {team}")
        
        return results
        
    except Exception as e:
        print(f"❌ Scraping error: {e}")
        return {}

def main():
    """Main test function"""
    print("🚀 Simple Match Scraper Test")
    print("=" * 50)
    
    # Test basic connectivity first
    if not simple_scrape_test():
        print("❌ Basic connectivity test failed")
        return
    
    # Test with common sports sites
    test_sites = [
        ("https://www.bbc.com/sport/football", "Real Madrid"),
        ("https://www.espn.com/soccer/", "Barcelona"),
        ("https://quotes.toscrape.com", "")  # Fallback
    ]
    
    for url, team in test_sites:
        print(f"\n" + "="*60)
        results = scrape_with_basic_selectors(url, team)
        
        if results:
            print(f"\n📊 Results Summary:")
            for data_type, items in results.items():
                print(f"   {data_type}: {len(items)} items found")
                if items:
                    print(f"      Sample: {items[0][:30]}...")
        else:
            print("❌ No results found")

if __name__ == "__main__":
    main()