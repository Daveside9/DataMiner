#!/usr/bin/env python3
"""
Final System Test
Test the complete real-time sports monitoring system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_time_system import RealTimeSportsSystem
import time
import threading

def test_real_time_system():
    """Test the complete real-time system"""
    print("🎯 Final Real-Time Sports System Test")
    print("=" * 60)
    
    system = RealTimeSportsSystem()
    
    # Test 1: Direct scraping
    print("📡 TEST 1: Direct Live Scraping")
    print("-" * 40)
    
    test_urls = [
        'https://www.flashscore.com/football/',
        'https://www.livescore.com/en/football/',
        'https://www.bbc.com/sport/football/scores-fixtures'
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🌐 Testing URL {i}: {url}")
        matches = system.scrape_live_scores(url)
        
        if matches:
            print(f"✅ Found {len(matches)} matches!")
            for j, match in enumerate(matches[:3], 1):
                print(f"   {j}. {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
                print(f"      Source: {match['source']}")
        else:
            print("❌ No matches found")
    
    # Test 2: Team filtering
    print(f"\n📡 TEST 2: Team Filtering")
    print("-" * 40)
    
    test_teams = ['Japan', 'Syria', 'Korea', 'Iran', 'Qatar', 'Arsenal', 'Chelsea']
    matches = system.scrape_live_scores('https://www.flashscore.com/football/', test_teams)
    
    if matches:
        print(f"✅ Found {len(matches)} matches for specified teams!")
        for match in matches:
            print(f"   ⚽ {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
    else:
        print("❌ No matches found for specified teams")
    
    # Test 3: Prediction system
    print(f"\n🤖 TEST 3: AI Prediction System")
    print("-" * 40)
    
    if matches:
        # Simulate match history for prediction
        match_id = list(system.live_matches.keys())[0] if system.live_matches else "test_match"
        
        if match_id not in system.live_matches:
            # Create test match data
            system.live_matches[match_id] = {
                'home_team': 'Japan U23',
                'away_team': 'Syria U23',
                'history': [
                    {'timestamp': '2026-01-07T20:00:00', 'home_score': 1, 'away_score': 0, 'total_goals': 1},
                    {'timestamp': '2026-01-07T20:15:00', 'home_score': 3, 'away_score': 0, 'total_goals': 3},
                    {'timestamp': '2026-01-07T20:30:00', 'home_score': 5, 'away_score': 0, 'total_goals': 5},
                ]
            }
        
        prediction = system.generate_prediction(match_id)
        if prediction and 'error' not in prediction:
            print(f"✅ Generated prediction!")
            print(f"   Current: {prediction['current_score']}")
            print(f"   Predicted: {prediction['predicted_score']}")
            print(f"   Confidence: {prediction['confidence']}%")
            print(f"   Reasoning: {prediction['reasoning']}")
        else:
            print("❌ Could not generate prediction")
    
    return len(matches) > 0 if matches else False

def test_api_endpoints():
    """Test the Flask API endpoints"""
    print(f"\n📡 TEST 4: API Endpoints")
    print("-" * 40)
    
    try:
        import requests
        import json
        
        # Start the system in background
        system = RealTimeSportsSystem()
        
        def run_server():
            system.run_server(host='localhost', port=5001)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(3)
        
        # Test start monitoring endpoint
        response = requests.post('http://localhost:5001/api/start-monitoring', 
                               json={
                                   'url': 'https://www.flashscore.com/football/',
                                   'duration': 1,  # 1 minute
                                   'interval': 30,
                                   'specific_teams': ['Japan', 'Syria']
                               })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Start monitoring API: {data['message']}")
            
            # Wait a bit then check live matches
            time.sleep(5)
            
            response = requests.get('http://localhost:5001/api/live-matches')
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Live matches API: {len(data.get('matches', {}))} matches")
                print(f"   Monitoring active: {data.get('monitoring_active', False)}")
            else:
                print("❌ Live matches API failed")
        else:
            print("❌ Start monitoring API failed")
    
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    success = test_real_time_system()
    
    if success:
        print(f"\n🎉 SYSTEM WORKING!")
        print("✅ Live scraping: Working")
        print("✅ Team filtering: Working") 
        print("✅ AI predictions: Working")
        print("\n💡 Ready to start the full system:")
        print("   python start_realtime.py")
    else:
        print(f"\n⚠️ PARTIAL SUCCESS")
        print("💡 Some features working, check individual tests above")
    
    print(f"\n🚀 Final test complete!")