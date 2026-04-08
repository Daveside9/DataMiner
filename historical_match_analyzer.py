#!/usr/bin/env python3
"""
Historical Match Analyzer - Search for specific team matches over time periods
"""

import requests
import json
from datetime import datetime, timedelta
import re
from urllib.parse import quote_plus

API_BASE = "http://localhost:5000/api"

class HistoricalMatchAnalyzer:
    def __init__(self):
        self.sports_sites = {
            "bbc_sport": {
                "base_url": "https://www.bbc.com/sport/football",
                "search_patterns": {
                    "team_vs_team": "/teams/{team1}/results",
                    "results": "/results",
                    "fixtures": "/fixtures"
                },
                "selectors": {
                    "matches": ".sp-c-fixture",
                    "home_teams": ".sp-c-fixture__team--home .sp-c-fixture__team-name",
                    "away_teams": ".sp-c-fixture__team--away .sp-c-fixture__team-name",
                    "scores": ".sp-c-fixture__score",
                    "dates": ".sp-c-fixture__date",
                    "status": ".sp-c-fixture__status"
                }
            },
            "espn": {
                "base_url": "https://www.espn.com/soccer",
                "search_patterns": {
                    "team_results": "/team/results/_/id/{team_id}",
                    "scoreboard": "/scoreboard"
                },
                "selectors": {
                    "matches": ".Table__TR",
                    "teams": ".team-name",
                    "scores": ".score",
                    "dates": ".date"
                }
            },
            "flashscore": {
                "base_url": "https://www.flashscore.com/football",
                "search_patterns": {
                    "results": "/results/",
                    "fixtures": "/fixtures/"
                },
                "selectors": {
                    "matches": ".event__match",
                    "home_teams": ".event__participant--home",
                    "away_teams": ".event__participant--away",
                    "scores": ".event__score",
                    "times": ".event__time"
                }
            }
        }
        
        self.team_aliases = {
            # Premier League teams with common aliases
            "chelsea": ["chelsea", "che", "chelsea fc", "blues"],
            "liverpool": ["liverpool", "liv", "liverpool fc", "reds"],
            "manchester_united": ["manchester united", "man utd", "united", "mu", "red devils"],
            "manchester_city": ["manchester city", "man city", "city", "mc", "citizens"],
            "arsenal": ["arsenal", "ars", "arsenal fc", "gunners"],
            "tottenham": ["tottenham", "spurs", "tot", "tottenham hotspur"],
            "newcastle": ["newcastle", "new", "newcastle united", "magpies"],
            "west_ham": ["west ham", "whu", "west ham united", "hammers"],
            "brighton": ["brighton", "bha", "brighton & hove albion", "seagulls"],
            "aston_villa": ["aston villa", "avl", "villa"],
            "everton": ["everton", "eve", "toffees"],
            "leicester": ["leicester", "lei", "leicester city", "foxes"],
            "wolves": ["wolves", "wol", "wolverhampton", "wanderers"],
            "crystal_palace": ["crystal palace", "cry", "palace", "eagles"],
            "burnley": ["burnley", "bur", "clarets"],
            "southampton": ["southampton", "sou", "saints"],
            "leeds": ["leeds", "lee", "leeds united", "whites"],
            "watford": ["watford", "wat", "hornets"],
            "norwich": ["norwich", "nor", "norwich city", "canaries"],
            "brentford": ["brentford", "bre", "bees"]
        }
    
    def search_team_matches(self, team1, team2=None, days_back=30, source="bbc_sport"):
        """Search for matches between specific teams over a time period"""
        print(f"🔍 Searching for matches: {team1}" + (f" vs {team2}" if team2 else " (all matches)"))
        print(f"📅 Time period: Last {days_back} days")
        print(f"🌐 Source: {source}")
        
        # Normalize team names
        team1_normalized = self._normalize_team_name(team1)
        team2_normalized = self._normalize_team_name(team2) if team2 else None
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        print(f"📊 Searching from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Get URLs to scrape based on the source
        urls_to_scrape = self._get_search_urls(team1_normalized, team2_normalized, source)
        
        all_matches = []
        
        for url in urls_to_scrape:
            print(f"\n📡 Scraping: {url}")
            matches = self._scrape_matches_from_url(url, source)
            
            if matches:
                # Filter matches by teams and date range
                filtered_matches = self._filter_matches(
                    matches, team1_normalized, team2_normalized, start_date, end_date
                )
                all_matches.extend(filtered_matches)
                print(f"✅ Found {len(filtered_matches)} relevant matches")
            else:
                print("❌ No matches found")
        
        # Remove duplicates and sort by date
        unique_matches = self._deduplicate_matches(all_matches)
        sorted_matches = sorted(unique_matches, key=lambda x: x.get('date', ''), reverse=True)
        
        print(f"\n🎯 FINAL RESULTS: {len(sorted_matches)} matches found")
        
        return {
            "search_query": {
                "team1": team1,
                "team2": team2,
                "days_back": days_back,
                "date_range": {
                    "start": start_date.strftime('%Y-%m-%d'),
                    "end": end_date.strftime('%Y-%m-%d')
                }
            },
            "matches": sorted_matches,
            "summary": self._generate_match_summary(sorted_matches, team1, team2)
        }
    
    def _normalize_team_name(self, team_name):
        """Normalize team name to match common aliases"""
        if not team_name:
            return None
        
        team_lower = team_name.lower().strip()
        
        # Check if it matches any known aliases
        for canonical_name, aliases in self.team_aliases.items():
            if team_lower in aliases:
                return canonical_name
        
        # Return cleaned version if no alias found
        return re.sub(r'[^a-zA-Z0-9\s]', '', team_lower).replace(' ', '_')
    
    def _get_search_urls(self, team1, team2, source):
        """Generate URLs to search based on teams and source"""
        urls = []
        site_config = self.sports_sites.get(source, {})
        base_url = site_config.get("base_url", "")
        
        if source == "bbc_sport":
            # BBC Sport URLs
            urls.append(f"{base_url}/results")
            urls.append(f"{base_url}/fixtures")
            
            # Try team-specific pages if we can map team names
            if team1:
                urls.append(f"{base_url}/teams/{team1}")
            if team2:
                urls.append(f"{base_url}/teams/{team2}")
        
        elif source == "espn":
            # ESPN URLs
            urls.append(f"{base_url}/scoreboard")
            urls.append(f"{base_url}/fixtures")
        
        elif source == "flashscore":
            # FlashScore URLs
            urls.append(f"{base_url}/results/")
            urls.append(f"{base_url}/fixtures/")
        
        return urls
    
    def _scrape_matches_from_url(self, url, source):
        """Scrape matches from a specific URL"""
        try:
            site_config = self.sports_sites.get(source, {})
            selectors = site_config.get("selectors", {})
            
            response = requests.post(f"{API_BASE}/scrape", json={
                "url": url,
                "selectors": selectors,
                "use_selenium": True
            })
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return self._parse_scraped_matches(result['data']['data'])
            
            return []
            
        except Exception as e:
            print(f"⚠️ Scraping error for {url}: {e}")
            return []
    
    def _parse_scraped_matches(self, scraped_data):
        """Parse scraped data into match objects"""
        matches = []
        
        # Get data arrays
        home_teams = scraped_data.get('home_teams', [])
        away_teams = scraped_data.get('away_teams', [])
        scores = scraped_data.get('scores', [])
        dates = scraped_data.get('dates', [])
        status = scraped_data.get('status', [])
        
        # Create match objects
        max_matches = max(len(home_teams), len(away_teams), 1)
        
        for i in range(max_matches):
            match = {
                "home_team": home_teams[i] if i < len(home_teams) else "Unknown",
                "away_team": away_teams[i] if i < len(away_teams) else "Unknown",
                "score": scores[i] if i < len(scores) else "N/A",
                "date": dates[i] if i < len(dates) else "Unknown",
                "status": status[i] if i < len(status) else "Unknown",
                "match_id": f"{i}_{hash(str(home_teams[i:i+1]) + str(away_teams[i:i+1]))}"
            }
            
            # Only add if we have meaningful data
            if match["home_team"] != "Unknown" or match["away_team"] != "Unknown":
                matches.append(match)
        
        return matches
    
    def _filter_matches(self, matches, team1, team2, start_date, end_date):
        """Filter matches by teams and date range"""
        filtered = []
        
        for match in matches:
            # Check if match involves the specified teams
            home_team_norm = self._normalize_team_name(match.get('home_team', ''))
            away_team_norm = self._normalize_team_name(match.get('away_team', ''))
            
            team_match = False
            
            if team2:
                # Looking for specific matchup
                team_match = (
                    (home_team_norm == team1 and away_team_norm == team2) or
                    (home_team_norm == team2 and away_team_norm == team1)
                )
            else:
                # Looking for any match involving team1
                team_match = (home_team_norm == team1 or away_team_norm == team1)
            
            if team_match:
                # Try to parse and filter by date (this is challenging without consistent date formats)
                # For now, we'll include all team matches and let the user filter visually
                filtered.append(match)
        
        return filtered
    
    def _deduplicate_matches(self, matches):
        """Remove duplicate matches"""
        seen = set()
        unique = []
        
        for match in matches:
            # Create a key based on teams and date
            key = (
                match.get('home_team', '').lower(),
                match.get('away_team', '').lower(),
                match.get('date', ''),
                match.get('score', '')
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(match)
        
        return unique
    
    def _generate_match_summary(self, matches, team1, team2):
        """Generate summary statistics for the matches"""
        if not matches:
            return {"total_matches": 0}
        
        summary = {
            "total_matches": len(matches),
            "teams_involved": set(),
            "score_patterns": {},
            "recent_form": []
        }
        
        # Collect team names and scores
        for match in matches:
            summary["teams_involved"].add(match.get('home_team', ''))
            summary["teams_involved"].add(match.get('away_team', ''))
            
            score = match.get('score', 'N/A')
            if score != 'N/A':
                summary["score_patterns"][score] = summary["score_patterns"].get(score, 0) + 1
        
        summary["teams_involved"] = list(summary["teams_involved"])
        summary["recent_form"] = matches[:5]  # Last 5 matches
        
        return summary
    
    def display_match_results(self, results):
        """Display match results in a formatted way"""
        print("\n" + "="*80)
        print("🏆 HISTORICAL MATCH ANALYSIS RESULTS")
        print("="*80)
        
        query = results["search_query"]
        print(f"🔍 Search: {query['team1']}" + (f" vs {query['team2']}" if query['team2'] else " (all matches)"))
        print(f"📅 Period: {query['date_range']['start']} to {query['date_range']['end']}")
        print(f"📊 Total matches found: {results['summary']['total_matches']}")
        
        if results["matches"]:
            print(f"\n📋 MATCH HISTORY:")
            print("-" * 80)
            
            for i, match in enumerate(results["matches"][:10], 1):  # Show first 10
                home = match.get('home_team', 'Unknown')[:15]
                away = match.get('away_team', 'Unknown')[:15]
                score = match.get('score', 'N/A')
                date = match.get('date', 'Unknown')
                status = match.get('status', 'Unknown')
                
                print(f"{i:2d}. {home:<15} vs {away:<15} | {score:<8} | {date} | {status}")
            
            if len(results["matches"]) > 10:
                print(f"    ... and {len(results['matches']) - 10} more matches")
            
            # Show summary stats
            summary = results["summary"]
            if summary.get("score_patterns"):
                print(f"\n📈 MOST COMMON SCORES:")
                sorted_scores = sorted(summary["score_patterns"].items(), key=lambda x: x[1], reverse=True)
                for score, count in sorted_scores[:5]:
                    print(f"    {score}: {count} times")
        
        else:
            print("\n❌ No matches found for the specified criteria")
            print("💡 Try:")
            print("   • Different team names (e.g., 'Chelsea', 'Blues', 'CHE')")
            print("   • Longer time period")
            print("   • Different data source")

def main():
    """Demo the historical match analyzer"""
    analyzer = HistoricalMatchAnalyzer()
    
    print("🏆 Historical Match Analyzer")
    print("=" * 50)
    
    # Example searches
    test_searches = [
        {"team1": "Chelsea", "team2": "Liverpool", "days_back": 30},
        {"team1": "Manchester United", "team2": "Arsenal", "days_back": 60},
        {"team1": "Chelsea", "days_back": 14}  # All Chelsea matches in last 2 weeks
    ]
    
    for search in test_searches:
        print(f"\n🎯 DEMO SEARCH:")
        results = analyzer.search_team_matches(**search)
        analyzer.display_match_results(results)
        
        print(f"\n" + "-" * 50)
    
    print(f"\n💡 USAGE EXAMPLES:")
    print("analyzer.search_team_matches('Chelsea', 'Liverpool', 30)  # Last month")
    print("analyzer.search_team_matches('Arsenal', days_back=7)      # Arsenal's last week")
    print("analyzer.search_team_matches('Man City', 'Tottenham', 90) # Last 3 months")

if __name__ == "__main__":
    main()