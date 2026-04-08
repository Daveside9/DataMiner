#!/usr/bin/env python3
"""
Test Enhanced Scraper
Quick test to see if the enhanced scraper can find live matches
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_scraper import EnhancedScraper

def test_scraper():
    """Test the enhanced scraper with live sites"""
    print("🧪 Testing Enhanced Scraper")
    print("=" * 60)
    
    scraper = EnhancedScraper()
    
    # Test URLs
    test_urls = [
        'https://www.livescore.com/en/football/',
        'https://www.flashscore.com/football/',
        'https://www.bbc.com/sport/football/scores-fixtures'
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🌐 TEST {i}: {url}")
        print("-" * 40)
        
        try:
            matches = scraper.scrape_live_scores(url)
            
            if matches:
                print(f"✅ SUCCESS: Found {len(matches)} live matches!")
                
                for j, match in enumerate(matches[:3], 1):
                    print(f"   {j}. {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
                    print(f"      Source: {match['source']}")
                    print(f"      Original: {match['original_score']}")
                
                if len(matches) > 3:
                    print(f"   ... and {len(matches) - 3} more matches")
                
                return True  # Found matches, test successful
            else:
                print("❌ No matches found")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("💡 If no matches found, it might be because:")
    print("   - No live matches are currently happening")
    print("   - Websites are blocking automated requests")
    print("   - JavaScript content requires Selenium (install selenium + webdriver-manager)")
    
    return False

def test_with_teams():
    """Test with specific team filtering"""
    print("\n🎯 Testing with specific teams...")
    
    scraper = EnhancedScraper()
    test_teams = ['Arsenal', 'Chelsea', 'Liverpool', 'Manchester']
    
    matches = scraper.scrape_live_scores(
        'https://www.livescore.com/en/football/',
        specific_teams=test_teams
    )
    
    if matches:
        print(f"✅ Found {len(matches)} matches for specified teams!")
        for match in matches:
            print(f"   ⚽ {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
    else:
        print("❌ No matches found for specified teams")

if __name__ == "__main__":
    success = test_scraper()
    
    if success:
        test_with_teams()
    
    print("\n🚀 Test complete!")