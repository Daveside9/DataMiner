#!/usr/bin/env python3
"""
Test Score Prediction API
"""

import requests
import json

def test_prediction_api():
    """Test the score prediction API"""
    print("🔮 Testing Score Prediction API")
    print("=" * 50)
    
    # Test 1: Direct prediction
    print("1️⃣ Testing direct score prediction...")
    try:
        response = requests.post('http://localhost:5003/api/predict-score', 
                               json={
                                   'home_team': 'Crystal Palace',
                                   'away_team': 'Manchester United',
                                   'league': 'Premier League',
                                   'odds_data': {
                                       "home_win": "1.66",
                                       "away_win": "1.32"
                                   }
                               },
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                prediction = result['prediction']
                print(f"✅ Prediction: {prediction['predicted_score']}")
                print(f"📊 Result: {prediction['result']}")
                print(f"🎲 Confidence: {prediction['confidence']}%")
                print(f"💭 Reasoning: {prediction['analysis']['reasoning']}")
            else:
                print(f"❌ Prediction failed: {result}")
        else:
            print(f"❌ API error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Direct prediction error: {e}")
    
    # Test 2: Bet9ja URL prediction
    print(f"\n2️⃣ Testing Bet9ja URL prediction...")
    try:
        bet9ja_url = "https://sports.bet9ja.com/mobile/eventdetail/zoomsoccer/premier-zoom/premier-zoom/z.crystalpalace-z.manunited/717892344/VS_1X2"
        
        response = requests.post('http://localhost:5003/api/predict-from-bet9ja', 
                               json={'url': bet9ja_url},
                               timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                prediction = result['prediction']
                bet9ja_data = result['bet9ja_data']
                
                print(f"✅ Bet9ja Extraction + Prediction Success!")
                print(f"🏠 Teams: {bet9ja_data['teams']['home_team']} vs {bet9ja_data['teams']['away_team']}")
                print(f"🎯 Predicted Score: {prediction['predicted_score']}")
                print(f"📊 Result: {prediction['result']} ({prediction['result_confidence']}% confidence)")
                print(f"🎲 Score Confidence: {prediction['confidence']}%")
                print(f"💭 Reasoning: {prediction['analysis']['reasoning']}")
                
                print(f"\n📈 Alternative Scores:")
                for alt in prediction['alternative_scores']:
                    print(f"   {alt['score']}: {alt['probability']}%")
                
                print(f"\n💰 Odds Used: {len(bet9ja_data.get('current_odds', {}))}")
                for market, odds in list(bet9ja_data.get('current_odds', {}).items())[:3]:
                    print(f"   {market}: {odds}")
            
            else:
                print(f"❌ Bet9ja prediction failed: {result.get('error')}")
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ Bet9ja prediction error: {e}")

if __name__ == "__main__":
    test_prediction_api()