#!/usr/bin/env python3
"""
Arsenal Match Analyzer
Get Arsenal's recent results and predict their next match using patterns
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

class ArsenalAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Arsenal-specific data sources
        self.data_sources = {
            'flashscore': 'https://www.flashscore.com/team/arsenal/WjYbghYs/',
            'bbc_sport': 'https://www.bbc.com/sport/football/teams/arsenal',
            'livescore': 'https://www.livescore.com/en/football/england/premier-league/arsenal/',
            'espn': 'https://www.espn.com/soccer/team/_/id/359/arsenal'
        }
        
        self.recent_results = []
        self.upcoming_fixtures = []
        self.patterns = {}
    
    def get_arsenal_recent_results(self):
        """Get Arsenal's recent match results from multiple sources"""
        print("🔍 Searching for Arsenal's recent results...")
        
        all_results = []
        
        # Try multiple sources
        for source_name, url in self.data_sources.items():
            print(f"📡 Checking {source_name}...")
            try:
                results = self.scrape_arsenal_from_source(url, source_name)
                if results:
                    all_results.extend(results)
                    print(f"✅ Found {len(results)} results from {source_name}")
                else:
                    print(f"❌ No results from {source_name}")
            except Exception as e:
                print(f"❌ Error with {source_name}: {e}")
        
        # Remove duplicates and sort by date
        unique_results = self.deduplicate_results(all_results)
        self.recent_results = sorted(unique_results, key=lambda x: x['date'], reverse=True)
        
        return self.recent_results
    
    def scrape_arsenal_from_source(self, url, source_name):
        """Scrape Arsenal data from a specific source"""
        results = []
        
        try:
            # Use Selenium for JavaScript-heavy sites
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            driver.get(url)
            time.sleep(5)  # Wait for page to load
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            text_content = soup.get_text()
            
            # Look for Arsenal match patterns
            arsenal_patterns = [
                r'Arsenal\s+(\d+)\s*[-–:]\s*(\d+)\s+([A-Z][a-zA-Z\s]+)',  # Arsenal 2-1 Chelsea
                r'([A-Z][a-zA-Z\s]+)\s+(\d+)\s*[-–:]\s*(\d+)\s+Arsenal',  # Chelsea 1-2 Arsenal
                r'Arsenal\s+vs?\s+([A-Z][a-zA-Z\s]+)\s+(\d+)\s*[-–:]\s*(\d+)',  # Arsenal vs Chelsea 2-1
            ]
            
            for pattern in arsenal_patterns:
                matches = re.finditer(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    try:
                        if 'Arsenal' in match.group(0):
                            # Determine if Arsenal was home or away
                            if match.group(0).lower().startswith('arsenal'):
                                # Arsenal was home
                                home_team = 'Arsenal'
                                away_team = match.group(3) if len(match.groups()) >= 3 else match.group(1)
                                home_score = int(match.group(1))
                                away_score = int(match.group(2))
                            else:
                                # Arsenal was away
                                home_team = match.group(1)
                                away_team = 'Arsenal'
                                home_score = int(match.group(2))
                                away_score = int(match.group(3))
                            
                            # Determine result for Arsenal
                            if home_team == 'Arsenal':
                                arsenal_score = home_score
                                opponent_score = away_score
                                venue = 'Home'
                            else:
                                arsenal_score = away_score
                                opponent_score = home_score
                                venue = 'Away'
                            
                            if arsenal_score > opponent_score:
                                result = 'Win'
                            elif arsenal_score < opponent_score:
                                result = 'Loss'
                            else:
                                result = 'Draw'
                            
                            opponent = away_team if home_team == 'Arsenal' else home_team
                            
                            match_data = {
                                'date': datetime.now() - timedelta(days=len(results)),  # Estimate dates
                                'opponent': opponent.strip(),
                                'venue': venue,
                                'arsenal_score': arsenal_score,
                                'opponent_score': opponent_score,
                                'result': result,
                                'score_line': f"{arsenal_score}-{opponent_score}",
                                'source': source_name
                            }
                            
                            results.append(match_data)
                    
                    except (ValueError, IndexError):
                        continue
            
            driver.quit()
            
        except Exception as e:
            print(f"❌ Scraping error for {source_name}: {e}")
        
        return results[:10]  # Return last 10 matches
    
    def deduplicate_results(self, results):
        """Remove duplicate results"""
        seen = set()
        unique_results = []
        
        for result in results:
            # Create a unique key based on opponent and score
            key = f"{result['opponent']}_{result['score_line']}_{result['venue']}"
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return unique_results
    
    def analyze_patterns(self):
        """Analyze Arsenal's recent patterns"""
        if not self.recent_results:
            return {}
        
        print("📊 Analyzing Arsenal's patterns...")
        
        patterns = {
            'recent_form': self.get_recent_form(),
            'home_away_record': self.get_home_away_record(),
            'scoring_patterns': self.get_scoring_patterns(),
            'result_trends': self.get_result_trends(),
            'opponent_analysis': self.get_opponent_analysis()
        }
        
        self.patterns = patterns
        return patterns
    
    def get_recent_form(self):
        """Get Arsenal's recent form (last 5-10 matches)"""
        recent_matches = self.recent_results[:10]
        
        form = {
            'wins': sum(1 for m in recent_matches if m['result'] == 'Win'),
            'draws': sum(1 for m in recent_matches if m['result'] == 'Draw'),
            'losses': sum(1 for m in recent_matches if m['result'] == 'Loss'),
            'goals_scored': sum(m['arsenal_score'] for m in recent_matches),
            'goals_conceded': sum(m['opponent_score'] for m in recent_matches),
            'matches_played': len(recent_matches)
        }
        
        if form['matches_played'] > 0:
            form['win_percentage'] = (form['wins'] / form['matches_played']) * 100
            form['avg_goals_scored'] = form['goals_scored'] / form['matches_played']
            form['avg_goals_conceded'] = form['goals_conceded'] / form['matches_played']
            form['goal_difference'] = form['goals_scored'] - form['goals_conceded']
        
        return form
    
    def get_home_away_record(self):
        """Analyze home vs away performance"""
        home_matches = [m for m in self.recent_results if m['venue'] == 'Home']
        away_matches = [m for m in self.recent_results if m['venue'] == 'Away']
        
        def analyze_venue(matches, venue_name):
            if not matches:
                return {'matches': 0}
            
            return {
                'matches': len(matches),
                'wins': sum(1 for m in matches if m['result'] == 'Win'),
                'draws': sum(1 for m in matches if m['result'] == 'Draw'),
                'losses': sum(1 for m in matches if m['result'] == 'Loss'),
                'goals_scored': sum(m['arsenal_score'] for m in matches),
                'goals_conceded': sum(m['opponent_score'] for m in matches),
                'win_rate': (sum(1 for m in matches if m['result'] == 'Win') / len(matches)) * 100
            }
        
        return {
            'home': analyze_venue(home_matches, 'Home'),
            'away': analyze_venue(away_matches, 'Away')
        }
    
    def get_scoring_patterns(self):
        """Analyze Arsenal's scoring patterns"""
        if not self.recent_results:
            return {}
        
        scores = [m['arsenal_score'] for m in self.recent_results]
        
        return {
            'most_common_scores': self.get_most_common_values(scores),
            'high_scoring_games': sum(1 for s in scores if s >= 3),
            'clean_sheets': sum(1 for m in self.recent_results if m['opponent_score'] == 0),
            'failed_to_score': sum(1 for s in scores if s == 0),
            'avg_goals_per_game': sum(scores) / len(scores) if scores else 0
        }
    
    def get_result_trends(self):
        """Analyze recent result trends"""
        if len(self.recent_results) < 3:
            return {}
        
        recent_5 = self.recent_results[:5]
        form_string = ''.join([m['result'][0] for m in recent_5])  # W, D, L
        
        return {
            'last_5_form': form_string,
            'current_streak': self.get_current_streak(),
            'longest_streak': self.get_longest_streak(),
            'momentum': self.calculate_momentum()
        }
    
    def get_current_streak(self):
        """Get current winning/losing streak"""
        if not self.recent_results:
            return {'type': 'None', 'length': 0}
        
        current_result = self.recent_results[0]['result']
        streak_length = 1
        
        for match in self.recent_results[1:]:
            if match['result'] == current_result:
                streak_length += 1
            else:
                break
        
        return {'type': current_result, 'length': streak_length}
    
    def get_longest_streak(self):
        """Get longest streak in recent matches"""
        if not self.recent_results:
            return {'type': 'None', 'length': 0}
        
        max_streak = 1
        max_type = self.recent_results[0]['result']
        current_streak = 1
        current_type = self.recent_results[0]['result']
        
        for match in self.recent_results[1:]:
            if match['result'] == current_type:
                current_streak += 1
            else:
                if current_streak > max_streak:
                    max_streak = current_streak
                    max_type = current_type
                current_streak = 1
                current_type = match['result']
        
        return {'type': max_type, 'length': max_streak}
    
    def calculate_momentum(self):
        """Calculate team momentum based on recent results"""
        if len(self.recent_results) < 3:
            return 0
        
        # Weight recent matches more heavily
        weights = [3, 2, 1]  # Most recent match has weight 3
        momentum = 0
        
        for i, match in enumerate(self.recent_results[:3]):
            if match['result'] == 'Win':
                momentum += 3 * weights[i]
            elif match['result'] == 'Draw':
                momentum += 1 * weights[i]
            # Loss adds 0
        
        max_possible = sum(weights) * 3
        return (momentum / max_possible) * 100
    
    def get_opponent_analysis(self):
        """Analyze performance against different types of opponents"""
        # This would be enhanced with more data about opponent strength
        opponents = {}
        for match in self.recent_results:
            opp = match['opponent']
            if opp not in opponents:
                opponents[opp] = {'matches': 0, 'wins': 0, 'goals_for': 0, 'goals_against': 0}
            
            opponents[opp]['matches'] += 1
            opponents[opp]['goals_for'] += match['arsenal_score']
            opponents[opp]['goals_against'] += match['opponent_score']
            
            if match['result'] == 'Win':
                opponents[opp]['wins'] += 1
        
        return opponents
    
    def get_most_common_values(self, values):
        """Get most common values in a list"""
        from collections import Counter
        counter = Counter(values)
        return counter.most_common(3)
    
    def predict_next_match(self, opponent=None, venue=None):
        """Predict Arsenal's next match result based on patterns"""
        if not self.patterns:
            self.analyze_patterns()
        
        print("🔮 Generating Arsenal next match prediction...")
        
        # Base prediction on recent form and patterns
        form = self.patterns['recent_form']
        home_away = self.patterns['home_away_record']
        scoring = self.patterns['scoring_patterns']
        trends = self.patterns['result_trends']
        
        # Calculate prediction confidence
        confidence_factors = []
        
        # Recent form factor
        if form['win_percentage'] > 60:
            confidence_factors.append(('Good recent form', 20))
        elif form['win_percentage'] < 30:
            confidence_factors.append(('Poor recent form', -15))
        
        # Home/Away factor
        if venue == 'Home' and home_away['home']['win_rate'] > 50:
            confidence_factors.append(('Strong at home', 15))
        elif venue == 'Away' and home_away['away']['win_rate'] > 50:
            confidence_factors.append(('Good away form', 10))
        
        # Momentum factor
        momentum = trends.get('momentum', 50)
        if momentum > 70:
            confidence_factors.append(('High momentum', 15))
        elif momentum < 30:
            confidence_factors.append(('Low momentum', -10))
        
        # Current streak factor
        streak = trends.get('current_streak', {})
        if streak.get('type') == 'Win' and streak.get('length', 0) >= 2:
            confidence_factors.append(('Winning streak', 10))
        elif streak.get('type') == 'Loss' and streak.get('length', 0) >= 2:
            confidence_factors.append(('Losing streak', -10))
        
        # Calculate base confidence
        base_confidence = 50
        for factor, value in confidence_factors:
            base_confidence += value
        
        # Clamp confidence between 20-90%
        confidence = max(20, min(90, base_confidence))
        
        # Predict most likely result
        if confidence > 65:
            predicted_result = 'Win'
        elif confidence > 45:
            predicted_result = 'Draw'
        else:
            predicted_result = 'Loss'
        
        # Predict score based on scoring patterns
        avg_goals = scoring.get('avg_goals_per_game', 1.5)
        predicted_arsenal_score = max(0, round(avg_goals))
        
        # Opponent score based on defensive record
        avg_conceded = form.get('avg_goals_conceded', 1.0)
        predicted_opponent_score = max(0, round(avg_conceded))
        
        # Adjust based on predicted result
        if predicted_result == 'Win':
            if predicted_arsenal_score <= predicted_opponent_score:
                predicted_arsenal_score = predicted_opponent_score + 1
        elif predicted_result == 'Loss':
            if predicted_arsenal_score >= predicted_opponent_score:
                predicted_opponent_score = predicted_arsenal_score + 1
        
        prediction = {
            'predicted_result': predicted_result,
            'predicted_score': f"{predicted_arsenal_score}-{predicted_opponent_score}",
            'confidence': confidence,
            'confidence_factors': confidence_factors,
            'opponent': opponent or 'Next Opponent',
            'venue': venue or 'TBD',
            'based_on_matches': len(self.recent_results),
            'key_stats': {
                'recent_win_rate': form.get('win_percentage', 0),
                'avg_goals_scored': form.get('avg_goals_scored', 0),
                'current_momentum': momentum,
                'current_streak': f"{streak.get('length', 0)} {streak.get('type', 'matches')}"
            }
        }
        
        return prediction
    
    def generate_report(self):
        """Generate comprehensive Arsenal analysis report"""
        print("📋 Generating Arsenal Analysis Report...")
        
        # Get data
        results = self.get_arsenal_recent_results()
        patterns = self.analyze_patterns()
        prediction = self.predict_next_match()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'team': 'Arsenal',
            'analysis_period': '12 hours / Recent matches',
            'recent_results': results[:5],  # Last 5 matches
            'patterns': patterns,
            'next_match_prediction': prediction,
            'summary': self.generate_summary(results, patterns, prediction)
        }
        
        return report
    
    def generate_summary(self, results, patterns, prediction):
        """Generate a summary of Arsenal's current situation"""
        if not results:
            return "No recent Arsenal data found."
        
        form = patterns.get('recent_form', {})
        
        summary = f"""
🔴 ARSENAL ANALYSIS SUMMARY:

📊 Recent Form ({form.get('matches_played', 0)} matches):
   • Wins: {form.get('wins', 0)} | Draws: {form.get('draws', 0)} | Losses: {form.get('losses', 0)}
   • Win Rate: {form.get('win_percentage', 0):.1f}%
   • Goals: {form.get('goals_scored', 0)} scored, {form.get('goals_conceded', 0)} conceded
   • Goal Difference: {form.get('goal_difference', 0):+d}

🔮 Next Match Prediction:
   • Result: {prediction['predicted_result']}
   • Score: Arsenal {prediction['predicted_score']}
   • Confidence: {prediction['confidence']}%
   • Key Factor: {prediction['confidence_factors'][0][0] if prediction['confidence_factors'] else 'Form analysis'}

📈 Current Momentum: {patterns.get('result_trends', {}).get('momentum', 0):.1f}%
        """.strip()
        
        return summary

def main():
    """Main function to run Arsenal analysis"""
    print("🔴 Arsenal Match Analyzer")
    print("=" * 60)
    
    analyzer = ArsenalAnalyzer()
    
    try:
        # Generate comprehensive report
        report = analyzer.generate_report()
        
        # Display results
        print("\n" + "=" * 60)
        print("📋 ARSENAL ANALYSIS REPORT")
        print("=" * 60)
        
        print(report['summary'])
        
        print(f"\n📅 Recent Results:")
        for i, match in enumerate(report['recent_results'][:5], 1):
            result_emoji = "✅" if match['result'] == 'Win' else "❌" if match['result'] == 'Loss' else "🟡"
            print(f"   {i}. {result_emoji} vs {match['opponent']} ({match['venue']}) - {match['score_line']} ({match['result']})")
        
        prediction = report['next_match_prediction']
        print(f"\n🔮 NEXT MATCH PREDICTION:")
        print(f"   Result: {prediction['predicted_result']}")
        print(f"   Score: Arsenal {prediction['predicted_score']}")
        print(f"   Confidence: {prediction['confidence']}%")
        print(f"   Based on: {prediction['based_on_matches']} recent matches")
        
        # Save report
        with open('arsenal_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Full report saved to: arsenal_analysis_report.json")
        print("✅ Arsenal analysis complete!")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    main()