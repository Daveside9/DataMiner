#!/usr/bin/env python3
"""
Test Comprehensive Team Analysis
"""

import requests
import json

def test_comprehensive_analysis():
    """Test the comprehensive team analysis API"""
    print("🚀 Testing Comprehensive Team Analysis")
    print("=" * 60)
    
    # Test URL
    test_url = "https://sports.bet9ja.com/mobile/eventdetail/zoomsoccer/premier-zoom/premier-zoom/z.crystalpalace-z.manunited/717892344/VS_1X2"
    
    print(f"🔍 Testing URL: {test_url}")
    print(f"📊 Expected: Crystal Palace vs Manchester United")
    
    try:
        response = requests.post('http://localhost:5003/api/analyze-teams-comprehensive', 
                               json={'url': test_url},
                               timeout=120)  # Longer timeout for comprehensive analysis
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                analysis = result['analysis']
                match_info = analysis['match_info']
                
                print(f"✅ Analysis Complete!")
                print(f"⚽ Match: {match_info['home_team']} vs {match_info['away_team']}")
                
                # Home team analysis
                home_analysis = analysis['home_team_analysis']
                print(f"\n🏠 {match_info['home_team']} Analysis:")
                if home_analysis.get('current_form'):
                    form = home_analysis['current_form']
                    print(f"   📊 Form: {form.get('form_string', 'N/A')} ({form.get('points', 0)} points)")
                    print(f"   📈 Form Rating: {form.get('form_rating', 'N/A')}/10")
                
                if home_analysis.get('league_position'):
                    pos = home_analysis['league_position']
                    print(f"   🏆 League Position: {pos.get('position', 'N/A')} ({pos.get('points', 0)} pts)")
                
                print(f"   ⚽ Last 5 Matches:")
                for i, match in enumerate(home_analysis.get('last_5_matches', [])[:5], 1):
                    result_emoji = "✅" if match['result'] == 'W' else "❌" if match['result'] == 'L' else "🟡"
                    print(f"     {i}. vs {match['opponent']}: {match['home_score']}-{match['away_score']} {result_emoji}")
                
                # Away team analysis
                away_analysis = analysis['away_team_analysis']
                print(f"\n🏃 {match_info['away_team']} Analysis:")
                if away_analysis.get('current_form'):
                    form = away_analysis['current_form']
                    print(f"   📊 Form: {form.get('form_string', 'N/A')} ({form.get('points', 0)} points)")
                    print(f"   📈 Form Rating: {form.get('form_rating', 'N/A')}/10")
                
                if away_analysis.get('league_position'):
                    pos = away_analysis['league_position']
                    print(f"   🏆 League Position: {pos.get('position', 'N/A')} ({pos.get('points', 0)} pts)")
                
                # Head-to-head
                h2h = analysis.get('head_to_head', {})
                if h2h.get('summary'):
                    summary = h2h['summary']
                    print(f"\n🔄 Head-to-Head Record (Last {summary.get('total_matches', 0)}):")
                    print(f"   🏠 {match_info['home_team']}: {summary.get('home_wins', 0)} wins")
                    print(f"   🏃 {match_info['away_team']}: {summary.get('away_wins', 0)} wins")
                    print(f"   🤝 Draws: {summary.get('draws', 0)}")
                
                # Predictions
                predictions = analysis.get('predictions', {})
                if predictions.get('match_result'):
                    result_pred = predictions['match_result']
                    print(f"\n🔮 Match Predictions:")
                    print(f"   🏠 Home Win: {result_pred.get('home_win', 0)}%")
                    print(f"   🤝 Draw: {result_pred.get('draw', 0)}%")
                    print(f"   🏃 Away Win: {result_pred.get('away_win', 0)}%")
                
                if predictions.get('total_goals'):
                    goals = predictions['total_goals']
                    print(f"\n⚽ Goals Predictions:")
                    print(f"   📈 Over 2.5: {goals.get('over_2_5', 0)}%")
                    print(f"   📉 Under 2.5: {goals.get('under_2_5', 0)}%")
                
                if predictions.get('both_teams_to_score'):
                    btts = predictions['both_teams_to_score']
                    print(f"   🎯 Both Teams to Score:")
                    print(f"     Yes: {btts.get('yes', 0)}%")
                    print(f"     No: {btts.get('no', 0)}%")
                
                if predictions.get('correct_scores'):
                    print(f"\n🎯 Most Likely Scores:")
                    for i, (score, prob) in enumerate(predictions['correct_scores'][:5], 1):
                        print(f"   {i}. {score}: {prob}%")
                
                if predictions.get('recommendation'):
                    print(f"\n💰 Betting Recommendations:")
                    for rec in predictions['recommendation']:
                        print(f"   • {rec}")
                
                # Betting insights
                betting = analysis.get('betting_insights', {})
                if betting.get('value_bets'):
                    print(f"\n💡 Value Betting Tips:")
                    for tip in betting['value_bets']:
                        print(f"   • {tip}")
                
                print(f"\n🎯 Risk Assessment: {betting.get('risk_assessment', 'N/A')}")
                print(f"🔒 Confidence Level: {betting.get('confidence_level', 'N/A')}")
                
            else:
                print(f"❌ Analysis failed: {result.get('error')}")
        
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_comprehensive_analysis()