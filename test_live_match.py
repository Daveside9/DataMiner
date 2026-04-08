#!/usr/bin/env python3
"""
Test Live Match Extraction
"""

import requests
import json

def test_live_match():
    """Test the live match URL"""
    print("⚽ Testing Live Match")
    print("=" * 50)
    
    live_url = "https://sports.bet9ja.com/mobile/liveEventDetail/soccer/soccerpremier-zoom/soccerpremier-zoom-premier-zoom/z.nottinghamforest-z.chelsea/8604989"
    
    print(f"🔍 Live Match URL: {live_url}")
    print(f"📊 Expected: Nottingham Forest vs Chelsea (currently 2-1)")
    
    try:
        # Test extraction
        response = requests.post('http://localhost:5003/api/extract-bet9ja-history', 
                               json={'url': live_url},
                               timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result['data']
                teams = data.get('teams', {})
                live_score = data.get('live_score')
                
                print(f"✅ Extraction Results:")
                print(f"   🏠 Home: {teams.get('home_team', 'Unknown')}")
                print(f"   🏃 Away: {teams.get('away_team', 'Unknown')}")
                print(f"   ⚽ Live Score: {live_score}")
                print(f"   💰 Odds: {len(data.get('current_odds', {}))}")
                
                # Test prediction
                print(f"\n🔮 Testing Prediction...")
                pred_response = requests.post('http://localhost:5003/api/predict-from-bet9ja', 
                                           json={'url': live_url},
                                           timeout=60)
                
                if pred_response.status_code == 200:
                    pred_result = pred_response.json()
                    if pred_result.get('success'):
                        prediction = pred_result['prediction']
                        print(f"   🎯 Predicted: {prediction['predicted_score']}")
                        print(f"   📊 Confidence: {prediction['confidence']}%")
                        print(f"   💭 Reasoning: {prediction['analysis']['reasoning']}")
                    else:
                        print(f"   ❌ Prediction failed: {pred_result.get('error')}")
                else:
                    print(f"   ❌ Prediction API error: {pred_response.status_code}")
            
            else:
                print(f"❌ Extraction failed: {result.get('error')}")
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_live_match()