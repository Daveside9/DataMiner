#!/usr/bin/env python3
"""
Test Team Filtering - Test the enhanced scraping with specific teams
"""

from real_time_system import RealTimeSportsSystem

def test_team_filtering():
    """Test scraping with specific team filters"""
    system = RealTimeSportsSystem()
    
    print("🧪 Testing Enhanced Scraping with Team Filtering")
    print("=" * 60)
    
    # Test different team combinations
    test_cases = [
        (['Arsenal', 'Chelsea'], 'Premier League teams'),
        (['Barcelona', 'Real Madrid'], 'La Liga teams'),
        (['Bayern', 'Dortmund'], 'Bundesliga teams'),
        ([], 'All teams')
    ]
    
    url = 'https://www.bbc.com/sport/football/scores-fixtures'
    
    for teams, description in test_cases:
        print(f"\n🎯 Testing: {description}")
        if teams:
            print(f"   Looking for: {', '.join(teams)}")
        else:
            print(f"   Looking for: All matches")
        
        result = system.scrape_live_scores(url, teams if teams else None)
        
        if result:
            print(f"✅ Found {len(result)} matches:")
            for match in result:
                print(f"   ⚽ {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
        else:
            print("❌ No matches found")
        
        print("-" * 40)
    
    print("\n💡 Summary:")
    print("- Enhanced scraping looks for ANY score patterns on the page")
    print("- Team filtering works by matching team names in the scraped data")
    print("- If no matches found, the website may not have live games right now")
    print("- Try during actual match times for best results")

if __name__ == "__main__":
    test_team_filtering()