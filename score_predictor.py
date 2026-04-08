#!/usr/bin/env python3
"""
AI Score Predictor
Advanced score prediction using team data, odds analysis, and historical patterns
"""

import random
import math
from datetime import datetime
import json

class ScorePredictor:
    def __init__(self):
        self.team_strengths = {
            # Premier League teams (approximate strength ratings)
            'arsenal': 85, 'chelsea': 82, 'liverpool': 88, 'manchester united': 80,
            'manchester city': 92, 'tottenham': 78, 'newcastle': 75, 'brighton': 70,
            'crystal palace': 65, 'west ham': 68, 'aston villa': 72, 'fulham': 67,
            'brentford': 63, 'wolves': 62, 'everton': 58, 'nottingham forest': 60,
            'bournemouth': 59, 'sheffield united': 45, 'burnley': 48, 'luton': 42,
            
            # Add more teams as needed
            'real madrid': 95, 'barcelona': 90, 'atletico madrid': 83,
            'bayern munich': 93, 'borussia dortmund': 81, 'psg': 89,
            'juventus': 79, 'ac milan': 77, 'inter milan': 80,
            
            # Nigerian teams
            'rivers united': 55, 'enyimba': 58, 'kano pillars': 52,
            'plateau united': 50, 'akwa united': 48
        }
        
        self.league_factors = {
            'premier league': 1.0,
            'premier zoom': 0.8,  # Virtual/zoom leagues typically lower scoring
            'champions league': 1.1,
            'europa league': 0.95,
            'la liga': 0.9,
            'bundesliga': 1.05,
            'serie a': 0.85,
            'ligue 1': 0.9,
            'npfl': 0.7  # Nigerian Professional Football League
        }
    
    def predict_match_score(self, home_team, away_team, league=None, odds_data=None, historical_data=None, live_score=None, is_live=False):
        """Predict match score using multiple factors"""
        
        print(f"🔮 Predicting: {home_team} vs {away_team}")
        
        if is_live and live_score:
            print(f"⚽ LIVE MATCH - Current Score: {live_score.get('home', 0)}-{live_score.get('away', 0)}")
            return self.predict_live_match_outcome(home_team, away_team, live_score, league, odds_data)
        
        # Normalize team names
        home_normalized = self.normalize_team_name(home_team)
        away_normalized = self.normalize_team_name(away_team)
        
        # Get team strengths
        home_strength = self.get_team_strength(home_normalized)
        away_strength = self.get_team_strength(away_normalized)
        
        print(f"📊 Team Strengths: {home_team}({home_strength}) vs {away_team}({away_strength})")
        
        # Apply home advantage
        home_strength += 5  # Home advantage boost
        
        # Apply league factor
        league_factor = self.get_league_factor(league)
        
        # Analyze odds if available
        odds_insight = self.analyze_odds(odds_data) if odds_data else {}
        
        # Calculate base goal expectancy
        home_goals_expected = self.calculate_goal_expectancy(home_strength, away_strength, league_factor)
        away_goals_expected = self.calculate_goal_expectancy(away_strength, home_strength, league_factor)
        
        # Apply odds adjustments
        if odds_insight:
            home_goals_expected *= odds_insight.get('home_factor', 1.0)
            away_goals_expected *= odds_insight.get('away_factor', 1.0)
        
        # Apply historical data if available
        if historical_data:
            historical_factor = self.analyze_historical_data(historical_data, home_team, away_team)
            home_goals_expected *= historical_factor.get('home_factor', 1.0)
            away_goals_expected *= historical_factor.get('away_factor', 1.0)
        
        # Generate multiple score predictions
        predictions = []
        confidence_scores = []
        
        for _ in range(100):  # Monte Carlo simulation
            home_goals = max(0, int(random.gauss(home_goals_expected, 0.8)))
            away_goals = max(0, int(random.gauss(away_goals_expected, 0.8)))
            predictions.append((home_goals, away_goals))
        
        # Find most likely scores
        score_frequency = {}
        for score in predictions:
            score_frequency[score] = score_frequency.get(score, 0) + 1
        
        # Get top 3 most likely scores
        top_scores = sorted(score_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Calculate confidence
        most_likely_score = top_scores[0][0]
        confidence = (top_scores[0][1] / len(predictions)) * 100
        
        # Generate result prediction
        home_score, away_score = most_likely_score
        if home_score > away_score:
            result = "Home Win"
            result_confidence = 60 + (home_strength - away_strength) * 0.5
        elif away_score > home_score:
            result = "Away Win"
            result_confidence = 60 + (away_strength - home_strength) * 0.5
        else:
            result = "Draw"
            result_confidence = 40
        
        result_confidence = min(95, max(55, result_confidence))
        
        prediction = {
            'match': f"{home_team} vs {away_team}",
            'predicted_score': f"{home_score}-{away_score}",
            'home_goals': home_score,
            'away_goals': away_score,
            'total_goals': home_score + away_score,
            'result': result,
            'confidence': round(confidence, 1),
            'result_confidence': round(result_confidence, 1),
            'prediction_type': 'live_analysis' if is_live else 'pre_match',
            'alternative_scores': [
                {'score': f"{score[0]}-{score[1]}", 'probability': round((freq/len(predictions))*100, 1)}
                for score, freq in top_scores[:3]
            ],
            'analysis': {
                'home_strength': home_strength,
                'away_strength': away_strength,
                'home_goals_expected': round(home_goals_expected, 2),
                'away_goals_expected': round(away_goals_expected, 2),
                'league_factor': league_factor,
                'odds_insight': odds_insight,
                'reasoning': self.generate_reasoning(home_team, away_team, home_strength, away_strength, odds_insight, is_live)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return prediction

    def predict_live_match_outcome(self, home_team, away_team, live_score, league=None, odds_data=None):
        """Predict final outcome for a live match"""
        
        current_home = live_score.get('home', 0)
        current_away = live_score.get('away', 0)
        current_total = current_home + current_away
        
        print(f"📊 Live Match Analysis - Current: {current_home}-{current_away}")
        
        # Estimate match progress (assume 90 minutes total)
        # This is a rough estimate - in reality you'd need actual time
        estimated_progress = min(0.8, current_total * 0.15 + 0.3)  # Rough estimate based on goals
        remaining_time_factor = 1.0 - estimated_progress
        
        # Get team strengths for remaining time analysis
        home_normalized = self.normalize_team_name(home_team)
        away_normalized = self.normalize_team_name(away_team)
        home_strength = self.get_team_strength(home_normalized)
        away_strength = self.get_team_strength(away_normalized)
        
        # Calculate expected additional goals
        league_factor = self.get_league_factor(league)
        
        # Reduced goal expectancy for remaining time
        additional_home_goals = self.calculate_goal_expectancy(home_strength, away_strength, league_factor) * remaining_time_factor
        additional_away_goals = self.calculate_goal_expectancy(away_strength, home_strength, league_factor) * remaining_time_factor
        
        # Account for current score psychology
        score_diff = current_home - current_away
        if score_diff > 1:  # Home team leading by 2+
            additional_away_goals *= 1.3  # Desperation factor
            additional_home_goals *= 0.8  # Conservative play
        elif score_diff < -1:  # Away team leading by 2+
            additional_home_goals *= 1.3
            additional_away_goals *= 0.8
        
        # Monte Carlo for final score
        final_scores = []
        for _ in range(100):
            add_home = max(0, int(random.gauss(additional_home_goals, 0.6)))
            add_away = max(0, int(random.gauss(additional_away_goals, 0.6)))
            
            final_home = current_home + add_home
            final_away = current_away + add_away
            final_scores.append((final_home, final_away))
        
        # Find most likely final scores
        score_frequency = {}
        for score in final_scores:
            score_frequency[score] = score_frequency.get(score, 0) + 1
        
        top_scores = sorted(score_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
        most_likely_final = top_scores[0][0]
        confidence = (top_scores[0][1] / len(final_scores)) * 100
        
        final_home, final_away = most_likely_final
        
        # Determine final result
        if final_home > final_away:
            result = "Home Win"
        elif final_away > final_home:
            result = "Away Win"
        else:
            result = "Draw"
        
        prediction = {
            'match': f"{home_team} vs {away_team}",
            'predicted_score': f"{final_home}-{final_away}",
            'home_goals': final_home,
            'away_goals': final_away,
            'total_goals': final_home + final_away,
            'result': result,
            'confidence': round(confidence, 1),
            'result_confidence': round(confidence * 1.2, 1),  # Higher confidence for live matches
            'prediction_type': 'live_final_score',
            'current_score': f"{current_home}-{current_away}",
            'additional_goals_predicted': {
                'home': final_home - current_home,
                'away': final_away - current_away
            },
            'alternative_scores': [
                {'score': f"{score[0]}-{score[1]}", 'probability': round((freq/len(final_scores))*100, 1)}
                for score, freq in top_scores[:3]
            ],
            'analysis': {
                'current_score': f"{current_home}-{current_away}",
                'estimated_progress': f"{estimated_progress*100:.0f}%",
                'remaining_time_factor': remaining_time_factor,
                'additional_home_expected': round(additional_home_goals, 2),
                'additional_away_expected': round(additional_away_goals, 2),
                'reasoning': f"Live match currently {current_home}-{current_away}. Based on team strengths and remaining time, predicting final score {final_home}-{final_away}. {result} most likely outcome."
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return prediction
    
    def normalize_team_name(self, team_name):
        """Normalize team name for lookup"""
        if not team_name:
            return ""
        
        # Handle common variations
        normalized = team_name.lower().strip()
        
        # Common replacements
        replacements = {
            'crystalpalace': 'crystal palace',
            'manunited': 'manchester united',
            'mancity': 'manchester city',
            'tottenham hotspur': 'tottenham',
            'spurs': 'tottenham',
            'man utd': 'manchester united',
            'man city': 'manchester city',
            'real': 'real madrid',
            'barca': 'barcelona',
            'bayern': 'bayern munich',
            'psg': 'psg',
            'juve': 'juventus'
        }
        
        return replacements.get(normalized, normalized)
    
    def get_team_strength(self, team_name):
        """Get team strength rating"""
        strength = self.team_strengths.get(team_name, 60)  # Default strength
        
        # Add some randomness for unknown teams
        if team_name not in self.team_strengths:
            strength += random.randint(-10, 10)
        
        return max(30, min(100, strength))
    
    def get_league_factor(self, league):
        """Get league scoring factor"""
        if not league:
            return 1.0
        
        league_normalized = league.lower().strip()
        return self.league_factors.get(league_normalized, 0.8)
    
    def calculate_goal_expectancy(self, team_strength, opponent_strength, league_factor):
        """Calculate expected goals for a team"""
        # Base calculation using team strengths
        strength_diff = team_strength - opponent_strength
        base_goals = 1.2 + (strength_diff / 50)  # Base around 1.2 goals
        
        # Apply league factor
        base_goals *= league_factor
        
        # Ensure reasonable range
        return max(0.3, min(4.0, base_goals))
    
    def analyze_odds(self, odds_data):
        """Analyze betting odds to extract insights"""
        if not odds_data or not isinstance(odds_data, dict):
            return {}
        
        insights = {'home_factor': 1.0, 'away_factor': 1.0}
        
        try:
            # Convert odds to probabilities and adjust expectations
            odds_values = []
            for market, odds_str in odds_data.items():
                try:
                    odds_val = float(odds_str)
                    if 1.0 <= odds_val <= 20.0:  # Reasonable odds range
                        odds_values.append(odds_val)
                except:
                    continue
            
            if odds_values:
                avg_odds = sum(odds_values) / len(odds_values)
                
                # Lower odds = higher probability = stronger team
                if avg_odds < 2.0:  # Favorite
                    insights['home_factor'] = 1.2
                    insights['away_factor'] = 0.8
                elif avg_odds > 3.0:  # Underdog
                    insights['home_factor'] = 0.8
                    insights['away_factor'] = 1.2
                
                insights['avg_odds'] = round(avg_odds, 2)
                insights['market_confidence'] = 'High' if len(odds_values) >= 2 else 'Low'
        
        except Exception as e:
            print(f"❌ Odds analysis error: {e}")
        
        return insights
    
    def analyze_historical_data(self, historical_data, home_team, away_team):
        """Analyze historical match data"""
        factors = {'home_factor': 1.0, 'away_factor': 1.0}
        
        try:
            if not historical_data or not isinstance(historical_data, list):
                return factors
            
            home_goals_avg = 0
            away_goals_avg = 0
            matches_count = 0
            
            for match in historical_data:
                if isinstance(match, dict):
                    score1 = match.get('score1', 0)
                    score2 = match.get('score2', 0)
                    
                    if isinstance(score1, int) and isinstance(score2, int):
                        home_goals_avg += score1
                        away_goals_avg += score2
                        matches_count += 1
            
            if matches_count > 0:
                home_goals_avg /= matches_count
                away_goals_avg /= matches_count
                
                # Adjust factors based on historical scoring
                if home_goals_avg > 1.5:
                    factors['home_factor'] = 1.1
                elif home_goals_avg < 1.0:
                    factors['home_factor'] = 0.9
                
                if away_goals_avg > 1.5:
                    factors['away_factor'] = 1.1
                elif away_goals_avg < 1.0:
                    factors['away_factor'] = 0.9
        
        except Exception as e:
            print(f"❌ Historical analysis error: {e}")
        
        return factors
    
    def generate_reasoning(self, home_team, away_team, home_strength, away_strength, odds_insight, is_live=False):
        """Generate human-readable reasoning for the prediction"""
        reasoning_parts = []
        
        if is_live:
            reasoning_parts.append("Live match analysis")
        
        # Team strength comparison
        strength_diff = home_strength - away_strength
        if strength_diff > 10:
            reasoning_parts.append(f"{home_team} has a significant strength advantage")
        elif strength_diff > 5:
            reasoning_parts.append(f"{home_team} has a slight edge in quality")
        elif strength_diff < -10:
            reasoning_parts.append(f"{away_team} is significantly stronger")
        elif strength_diff < -5:
            reasoning_parts.append(f"{away_team} has better form/quality")
        else:
            reasoning_parts.append("Teams are evenly matched")
        
        # Home advantage (only for non-live or if not specified)
        if not is_live:
            reasoning_parts.append("Home advantage factored in")
        
        # Odds insight
        if odds_insight.get('avg_odds'):
            avg_odds = odds_insight['avg_odds']
            if avg_odds < 2.0:
                reasoning_parts.append("Betting markets favor home team")
            elif avg_odds > 3.0:
                reasoning_parts.append("Betting markets favor away team")
            else:
                reasoning_parts.append("Betting markets see close contest")
        
        return ". ".join(reasoning_parts) + "."

def test_score_predictor():
    """Test the score predictor"""
    print("🔮 Testing Score Predictor")
    print("=" * 50)
    
    predictor = ScorePredictor()
    
    # Test with Crystal Palace vs Man United (from Bet9ja data)
    odds_data = {
        "1.664.254.80": "1.66",
        "9.205.301.32": "1.32"
    }
    
    prediction = predictor.predict_match_score(
        home_team="Crystal Palace",
        away_team="Manchester United", 
        league="Premier League",
        odds_data=odds_data
    )
    
    print(f"🎯 Prediction: {prediction['predicted_score']}")
    print(f"📊 Result: {prediction['result']}")
    print(f"🎲 Confidence: {prediction['confidence']}%")
    print(f"💭 Reasoning: {prediction['analysis']['reasoning']}")
    
    print(f"\n📈 Alternative Scores:")
    for alt in prediction['alternative_scores']:
        print(f"   {alt['score']}: {alt['probability']}%")
    
    return prediction

if __name__ == "__main__":
    test_score_predictor()