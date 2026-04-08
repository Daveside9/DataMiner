#!/usr/bin/env python3
"""
Sports Analytics System - Advanced sports data collection and pattern analysis
"""

import requests
import json
import time
from datetime import datetime, timedelta
import pandas as pd

API_BASE = "http://localhost:5000/api"

class SportsAnalytics:
    def __init__(self):
        self.sports_configs = {
            "premier_league_results": {
                "url": "https://www.premierleague.com/results",
                "selectors": {
                    "home_teams": ".match-fixture__team--home .match-fixture__short-name",
                    "away_teams": ".match-fixture__team--away .match-fixture__short-name", 
                    "home_scores": ".match-fixture__team--home .match-fixture__score",
                    "away_scores": ".match-fixture__team--away .match-fixture__score",
                    "match_dates": ".match-fixture__date",
                    "match_status": ".match-fixture__status"
                }
            },
            "bbc_football": {
                "url": "https://www.bbc.com/sport/football/scores-fixtures",
                "selectors": {
                    "matches": ".gs-o-list-ui__item",
                    "teams": ".sp-c-fixture__team-name-trunc",
                    "scores": ".sp-c-fixture__number--home, .sp-c-fixture__number--away",
                    "times": ".sp-c-fixture__status-wrapper",
                    "competitions": ".sp-c-fixture__competition"
                }
            },
            "espn_soccer": {
                "url": "https://www.espn.com/soccer/scoreboard",
                "selectors": {
                    "team_names": ".ScoreCell__TeamName",
                    "scores": ".ScoreCell__Score", 
                    "match_times": ".ScoreCell__Time",
                    "match_status": ".ScoreCell__GameStatus"
                }
            },
            "flashscore": {
                "url": "https://www.flashscore.com/football/",
                "selectors": {
                    "home_teams": ".event__participant--home",
                    "away_teams": ".event__participant--away",
                    "scores": ".event__score",
                    "times": ".event__time",
                    "leagues": ".event__title"
                }
            }
        }
    
    def scrape_sports_data(self, config_name, use_selenium=True):
        """Scrape sports data from a configured source"""
        if config_name not in self.sports_configs:
            print(f"❌ Unknown sports config: {config_name}")
            return None
        
        config = self.sports_configs[config_name]
        
        print(f"⚽ Scraping {config_name}...")
        print(f"📡 URL: {config['url']}")
        
        data = {
            "url": config['url'],
            "selectors": config['selectors'],
            "use_selenium": use_selenium
        }
        
        try:
            response = requests.post(f"{API_BASE}/scrape", json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ Sports data scraped successfully!")
                    return self._process_sports_data(result, config_name)
                else:
                    print(f"❌ Scraping failed: {result.get('error')}")
                    return None
            else:
                print(f"❌ Request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def _process_sports_data(self, raw_data, source):
        """Process and structure sports data"""
        scraped_data = raw_data['data']['data']
        
        processed = {
            "source": source,
            "timestamp": raw_data['timestamp'],
            "matches": [],
            "summary": {}
        }
        
        # Try to pair teams and scores
        home_teams = scraped_data.get('home_teams', []) or scraped_data.get('team_names', [])[::2] if scraped_data.get('team_names') else []
        away_teams = scraped_data.get('away_teams', []) or scraped_data.get('team_names', [])[1::2] if scraped_data.get('team_names') else []
        scores = scraped_data.get('scores', []) or scraped_data.get('home_scores', []) + scraped_data.get('away_scores', [])
        times = scraped_data.get('times', []) or scraped_data.get('match_times', []) or scraped_data.get('match_dates', [])
        
        # Create match objects
        max_matches = min(len(home_teams), len(away_teams)) if home_teams and away_teams else 0
        
        for i in range(max_matches):
            match = {
                "home_team": home_teams[i] if i < len(home_teams) else "Unknown",
                "away_team": away_teams[i] if i < len(away_teams) else "Unknown",
                "score": scores[i] if i < len(scores) else "N/A",
                "time": times[i] if i < len(times) else "N/A",
                "match_id": f"{source}_{i}_{int(time.time())}"
            }
            processed["matches"].append(match)
        
        # Generate summary
        processed["summary"] = {
            "total_matches": len(processed["matches"]),
            "data_points": sum(len(v) if isinstance(v, list) else 1 for v in scraped_data.values()),
            "source_url": raw_data['data']['url']
        }
        
        print(f"📊 Processed {len(processed['matches'])} matches")
        return processed
    
    def collect_historical_sports_data(self, config_name, intervals=5, delay_minutes=30):
        """Collect sports data over time for trend analysis"""
        print(f"📅 Starting historical sports data collection")
        print(f"⚽ Source: {config_name}")
        print(f"🕐 Intervals: {intervals} collections every {delay_minutes} minutes")
        
        historical_data = []
        
        for i in range(intervals):
            print(f"\n📡 Collection {i+1}/{intervals} - {datetime.now().strftime('%H:%M:%S')}")
            
            data = self.scrape_sports_data(config_name)
            
            if data:
                historical_data.append(data)
                print(f"✅ Collected {data['summary']['total_matches']} matches")
                
                # Store in database with source name
                self._store_sports_data(data, config_name)
            else:
                print(f"❌ Collection {i+1} failed")
            
            if i < intervals - 1:
                print(f"⏳ Waiting {delay_minutes} minutes until next collection...")
                time.sleep(delay_minutes * 60)  # Convert to seconds
        
        print(f"\n🎯 Historical collection complete: {len(historical_data)} successful collections")
        return historical_data
    
    def _store_sports_data(self, processed_data, source_name):
        """Store processed sports data in database"""
        try:
            # Add data source if not exists
            requests.post(f"{API_BASE}/sources", json={
                "name": source_name,
                "url": self.sports_configs[source_name]["url"],
                "description": f"Sports data from {source_name}"
            })
            
            # Store the processed data
            storage_data = {
                "url": self.sports_configs[source_name]["url"],
                "data": processed_data
            }
            
            response = requests.post(f"{API_BASE}/scrape", json=storage_data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"⚠️ Storage warning: {e}")
            return False
    
    def analyze_sports_patterns(self, source_name):
        """Analyze patterns in collected sports data"""
        print(f"📊 Analyzing sports patterns for {source_name}...")
        
        try:
            # Get historical data
            response = requests.get(f"{API_BASE}/data/{source_name}")
            
            if response.status_code == 200:
                historical_data = response.json().get("data", [])
                
                if not historical_data:
                    print("❌ No historical data found. Collect some data first!")
                    return None
                
                # Analyze patterns
                analysis_response = requests.get(f"{API_BASE}/analyze/{source_name}")
                
                if analysis_response.status_code == 200:
                    analysis = analysis_response.json().get("analysis", {})
                    
                    # Add sports-specific analysis
                    sports_analysis = self._analyze_sports_specific_patterns(historical_data)
                    analysis["sports_insights"] = sports_analysis
                    
                    self._display_sports_analysis(analysis)
                    return analysis
                else:
                    print("❌ Pattern analysis failed")
                    return None
            else:
                print("❌ Could not retrieve historical data")
                return None
                
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return None
    
    def _analyze_sports_specific_patterns(self, historical_data):
        """Analyze sports-specific patterns"""
        sports_insights = {
            "match_frequency": {},
            "score_patterns": {},
            "team_performance": {},
            "time_patterns": {}
        }
        
        all_matches = []
        for entry in historical_data:
            if 'data' in entry and 'matches' in entry['data']:
                all_matches.extend(entry['data']['matches'])
        
        if not all_matches:
            return sports_insights
        
        # Analyze match frequency
        dates = [entry['timestamp'][:10] for entry in historical_data]
        sports_insights["match_frequency"] = {
            "total_collections": len(historical_data),
            "total_matches_found": len(all_matches),
            "avg_matches_per_collection": len(all_matches) / len(historical_data) if historical_data else 0
        }
        
        # Analyze teams
        teams = {}
        for match in all_matches:
            home_team = match.get('home_team', 'Unknown')
            away_team = match.get('away_team', 'Unknown')
            
            teams[home_team] = teams.get(home_team, 0) + 1
            teams[away_team] = teams.get(away_team, 0) + 1
        
        sports_insights["team_performance"] = {
            "most_frequent_teams": sorted(teams.items(), key=lambda x: x[1], reverse=True)[:10],
            "total_unique_teams": len(teams)
        }
        
        return sports_insights
    
    def _display_sports_analysis(self, analysis):
        """Display sports analysis results"""
        print("\n" + "="*60)
        print("🏆 SPORTS ANALYTICS REPORT")
        print("="*60)
        
        # General insights
        insights = analysis.get("insights", [])
        if insights:
            print("\n💡 KEY INSIGHTS:")
            for insight in insights:
                print(f"  • {insight}")
        
        # Sports-specific insights
        sports_insights = analysis.get("sports_insights", {})
        
        if "match_frequency" in sports_insights:
            freq = sports_insights["match_frequency"]
            print(f"\n⚽ MATCH FREQUENCY ANALYSIS:")
            print(f"  • Total data collections: {freq.get('total_collections', 0)}")
            print(f"  • Total matches found: {freq.get('total_matches_found', 0)}")
            print(f"  • Average matches per collection: {freq.get('avg_matches_per_collection', 0):.1f}")
        
        if "team_performance" in sports_insights:
            teams = sports_insights["team_performance"]
            print(f"\n🏅 TEAM ANALYSIS:")
            print(f"  • Total unique teams: {teams.get('total_unique_teams', 0)}")
            
            most_frequent = teams.get('most_frequent_teams', [])
            if most_frequent:
                print("  • Most frequently appearing teams:")
                for team, count in most_frequent[:5]:
                    print(f"    - {team}: {count} appearances")
        
        # Summary statistics
        summary = analysis.get("summary", {})
        if summary:
            print(f"\n📈 DATA SUMMARY:")
            print(f"  • Total records: {summary.get('total_records', 0)}")
            print(f"  • Success rate: {summary.get('success_rate', 0):.1%}")
            print(f"  • Data collection period: {summary.get('date_range', {}).get('days', 0)} days")

def main():
    """Demo the sports analytics system"""
    analytics = SportsAnalytics()
    
    print("🏆 Sports Analytics System")
    print("=" * 50)
    
    # Show available configurations
    print("📋 Available sports data sources:")
    for name, config in analytics.sports_configs.items():
        print(f"  • {name}: {config['url']}")
    
    print(f"\n🎯 DEMO: Let's analyze BBC Football data")
    
    # Test single scrape
    print("\n1️⃣ Single data collection...")
    result = analytics.scrape_sports_data("bbc_football")
    
    if result:
        print(f"✅ Found {result['summary']['total_matches']} matches")
    
    # Simulate historical collection (shorter intervals for demo)
    print(f"\n2️⃣ Historical data collection (3 samples, 10 second intervals)...")
    historical = analytics.collect_historical_sports_data("bbc_football", intervals=3, delay_minutes=0.17)  # ~10 seconds
    
    # Analyze patterns
    print(f"\n3️⃣ Pattern analysis...")
    analysis = analytics.analyze_sports_patterns("bbc_football")
    
    print(f"\n🎉 Sports Analytics Demo Complete!")
    print(f"\n💡 To use with your own sports website:")
    print(f"1. Add your sports site to sports_configs")
    print(f"2. Define CSS selectors for teams, scores, dates")
    print(f"3. Run: analytics.collect_historical_sports_data('your_site', 10, 60)")
    print(f"4. Analyze: analytics.analyze_sports_patterns('your_site')")

if __name__ == "__main__":
    main()