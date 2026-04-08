#!/usr/bin/env python3
"""
Example: How to analyze YOUR sports website
"""

import requests
import time

API_BASE = "http://localhost:5000/api"

def analyze_your_sports_site():
    """Example: Analyze any sports website"""
    
    # STEP 1: Define your sports website
    your_sports_site = {
        "url": "https://www.livescore.com/",  # Replace with your site
        "selectors": {
            # Customize these CSS selectors for your site:
            "home_teams": ".home-team, .team-home, .fixture-home",
            "away_teams": ".away-team, .team-away, .fixture-away", 
            "scores": ".score, .result, .match-score",
            "times": ".time, .date, .match-time, .kick-off",
            "leagues": ".league, .competition, .tournament"
        }
    }
    
    print("⚽ CUSTOM SPORTS ANALYTICS")
    print("=" * 50)
    print(f"🎯 Target: {your_sports_site['url']}")
    
    # STEP 2: Collect historical data
    print("\n📊 Starting historical data collection...")
    
    collections = []
    intervals = 5  # Number of collections
    delay = 30     # Seconds between collections (use 3600 for hourly)
    
    for i in range(intervals):
        print(f"\n📡 Collection {i+1}/{intervals}")
        
        # Scrape current data
        response = requests.post(f"{API_BASE}/scrape", json={
            "url": your_sports_site["url"],
            "selectors": your_sports_site["selectors"],
            "use_selenium": True  # Use for dynamic content
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                collections.append(result)
                
                # Show what we found
                data = result['data']['data']
                print(f"✅ Success! Found:")
                for key, value in data.items():
                    if isinstance(value, list) and value:
                        print(f"  • {key}: {len(value)} items")
                        print(f"    Sample: {value[0][:50]}...")
                    elif value:
                        print(f"  • {key}: {str(value)[:50]}...")
            else:
                print(f"❌ Failed: {result.get('error')}")
        
        # Wait between collections
        if i < intervals - 1:
            print(f"⏳ Waiting {delay} seconds...")
            time.sleep(delay)
    
    # STEP 3: Analyze patterns
    print(f"\n📈 PATTERN ANALYSIS")
    print("=" * 30)
    
    if collections:
        print(f"✅ Collected {len(collections)} data samples")
        
        # Analyze team frequency
        all_teams = []
        all_scores = []
        
        for collection in collections:
            data = collection['data']['data']
            
            # Extract teams
            home_teams = data.get('home_teams', [])
            away_teams = data.get('away_teams', [])
            all_teams.extend(home_teams + away_teams)
            
            # Extract scores
            scores = data.get('scores', [])
            all_scores.extend(scores)
        
        # Show team frequency
        if all_teams:
            team_counts = {}
            for team in all_teams:
                if team and team.strip():
                    team_counts[team] = team_counts.get(team, 0) + 1
            
            print(f"\n🏅 MOST FREQUENT TEAMS:")
            sorted_teams = sorted(team_counts.items(), key=lambda x: x[1], reverse=True)
            for team, count in sorted_teams[:10]:
                print(f"  • {team}: {count} appearances")
        
        # Show score patterns
        if all_scores:
            print(f"\n⚽ SCORE PATTERNS:")
            print(f"  • Total scores found: {len(all_scores)}")
            print(f"  • Sample scores: {all_scores[:5]}")
        
        # Time-based patterns
        collection_times = [c['timestamp'] for c in collections]
        print(f"\n🕐 COLLECTION TIMELINE:")
        for i, timestamp in enumerate(collection_times):
            print(f"  • Collection {i+1}: {timestamp}")
        
        print(f"\n💡 INSIGHTS:")
        print(f"  • Data collection success rate: {len(collections)}/{intervals} ({len(collections)/intervals*100:.1f}%)")
        print(f"  • Average data points per collection: {sum(len(str(c)) for c in collections) / len(collections):.0f} characters")
        print(f"  • Unique teams discovered: {len(set(all_teams)) if all_teams else 0}")
        
    else:
        print("❌ No data collected. Check your CSS selectors!")
    
    return collections

def main():
    """Run the custom sports analysis"""
    print("🚀 Custom Sports Website Analyzer")
    print("🎯 This will analyze YOUR sports website!")
    print("\n💡 Instructions:")
    print("1. Edit the 'your_sports_site' dictionary above")
    print("2. Set your website URL")
    print("3. Customize CSS selectors for your site")
    print("4. Run this script!")
    
    # Check API connection
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("\n✅ DataMiner API is running")
            
            # Run the analysis
            analyze_your_sports_site()
            
        else:
            print("\n❌ DataMiner API not responding")
    except:
        print("\n❌ Cannot connect to DataMiner API")
        print("Make sure to run: python backend/app.py")

if __name__ == "__main__":
    main()