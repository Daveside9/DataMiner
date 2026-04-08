#!/usr/bin/env python3
"""
Sports Data Collector - Specialized scraper for sports websites
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:5000/api"

class SportsDataCollector:
    def __init__(self):
        self.sports_sites = {
            "bbc_sport": {
                "url": "https://www.bbc.com/sport/football/scores-fixtures",
                "selectors": {
                    "matches": ".gs-o-list-ui__item",
                    "teams": ".gs-u-display-none\\@m .sp-c-fixture__team-name-trunc",
                    "scores": ".sp-c-fixture__number--home, .sp-c-fixture__number--away",
                    "status": ".sp-c-fixture__status"
                }
            },
            "espn": {
                "url": "https://www.espn.com/soccer/scoreboard",
                "selectors": {
                    "matches": ".ScoreCell",
                    "teams": ".ScoreCell__TeamName",
                    "scores": ".ScoreCell__Score",
                    "time": ".ScoreCell__Time"
                }
            },
            "premier_league": {
                "url": "https://www.premierleague.com/fixtures",
                "selectors": {
                    "fixtures": ".fixture",
                    "home_teams": ".home .long",
                    "away_teams": ".away .long", 
                    "scores": ".score",
                    "kickoff": ".kickoff"
                }
            }
        }
    
    def scrape_sports_site(self, site_name, use_selenium=False):
        """Scrape a specific sports site"""
        if site_name not in self.sports_sites:
            print(f"❌ Unknown site: {site_name}")
            return None
        
        site_config = self.sports_sites[site_name]
        
        print(f"🏈 Scraping {site_name}...")
        print(f"📡 URL: {site_config['url']}")
        
        data = {
            "url": site_config['url'],
            "selectors": site_config['selectors'],
            "use_selenium": use_selenium
        }
        
        try:
            response = requests.post(f"{API_BASE}/scrape", json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ Scraping successful!")
                    return result
                else:
                    print(f"❌ Scraping failed: {result.get('error')}")
                    return None
            else:
                print(f"❌ Request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def analyze_sports_data(self, site_name):
        """Analyze scraped sports data for patterns"""
        print(f"\n📊 Analyzing {site_name} data...")
        
        try:
            response = requests.get(f"{API_BASE}/analyze/{site_name}")
            
            if response.status_code == 200:
                analysis = response.json()
                print("✅ Analysis complete!")
                return analysis
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return None
    
    def collect_historical_data(self, site_name, intervals=5, delay=60):
        """Collect data at regular intervals for pattern analysis"""
        print(f"🕐 Starting historical data collection for {site_name}")
        print(f"📅 Will collect {intervals} samples with {delay}s delay")
        
        results = []
        
        for i in range(intervals):
            print(f"\n📡 Collection {i+1}/{intervals}")
            result = self.scrape_sports_site(site_name)
            
            if result:
                results.append(result)
                print(f"✅ Sample {i+1} collected")
            else:
                print(f"❌ Sample {i+1} failed")
            
            if i < intervals - 1:  # Don't wait after last collection
                print(f"⏳ Waiting {delay} seconds...")
                time.sleep(delay)
        
        print(f"\n🎯 Historical collection complete: {len(results)} samples")
        return results

def main():
    """Demo the sports data collector"""
    collector = SportsDataCollector()
    
    print("🏈 Sports Data Collector Demo")
    print("=" * 40)
    
    # List available sites
    print("📋 Available sports sites:")
    for site_name, config in collector.sports_sites.items():
        print(f"  • {site_name}: {config['url']}")
    
    # Test scraping one site
    print(f"\n🧪 Testing with BBC Sport...")
    result = collector.scrape_sports_site("bbc_sport", use_selenium=True)
    
    if result:
        print(f"\n📊 Data Summary:")
        data = result['data']['data']
        for key, value in data.items():
            if isinstance(value, list):
                print(f"  {key}: {len(value)} items")
            else:
                print(f"  {key}: {str(value)[:50]}...")
    
    print(f"\n💡 Next Steps:")
    print("1. Run historical collection: collector.collect_historical_data('bbc_sport', 3, 30)")
    print("2. Analyze patterns: collector.analyze_sports_data('bbc_sport')")
    print("3. Try different sports sites with different selectors")

if __name__ == "__main__":
    main()