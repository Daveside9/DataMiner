#!/usr/bin/env python3
"""
Test Working System
Test with Flashscore which we know has live matches
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_time_system import RealTimeSportsSystem

def test_working_system():
    """Test the system with Flashscore"""
    print("🧪 Testing Working System with Flashscore")
    print("=" * 60)
    
    system = RealTimeSportsSystem()
    
    # Test with Flashscore (we know this works)
    print("🌐 Testing Flashscore (known working)...")
    matches = system.scrape_live_scores('https://www.flashscore.com/football/')
    
    if matches:
        print(f"✅ SUCCESS: Found {len(matches)} live matches!")
        
        for i, match in enumerate(matches[:5], 1):
            print(f"   {i}. {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
            print(f"      Source: {match['source']}")
            print(f"      Time: {match['timestamp']}")
        
        # Test team filtering with the found teams
        if matches:
            # Extract team names from found matches
            team_names = []
            for match in matches[:3]:
                team_names.extend([match['home_team'], match['away_team']])
            
            # Test filtering with first team
            if team_names:
                test_team = team_names[0].split()[0]  # First word of first team
                print(f"\n🎯 Testing team filter with '{test_team}'...")
                
                filtered_matches = system.scrape_live_scores(
                    'https://www.flashscore.com/football/', 
                    [test_team]
                )
                
                if filtered_matches:
                    print(f"✅ Team filtering works: Found {len(filtered_matches)} matches for '{test_team}'")
                    for match in filtered_matches:
                        print(f"   ⚽ {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
                else:
                    print(f"❌ No matches found for team filter '{test_team}'")
        
        # Test prediction system
        print(f"\n🤖 Testing AI Prediction System...")
        
        # Create test match history
        test_match_id = "test_match_for_prediction"
        system.live_matches[test_match_id] = {
            'home_team': matches[0]['home_team'],
            'away_team': matches[0]['away_team'],
            'history': [
                {'timestamp': '2026-01-07T20:00:00', 'home_score': 0, 'away_score': 0, 'total_goals': 0},
                {'timestamp': '2026-01-07T20:15:00', 'home_score': 1, 'away_score': 0, 'total_goals': 1},
                {'timestamp': '2026-01-07T20:30:00', 'home_score': matches[0]['home_score'], 'away_score': matches[0]['away_score'], 'total_goals': matches[0]['total_goals']},
            ]
        }
        
        prediction = system.generate_prediction(test_match_id)
        if prediction and 'error' not in prediction:
            print(f"✅ AI Prediction generated!")
            print(f"   Match: {matches[0]['home_team']} vs {matches[0]['away_team']}")
            print(f"   Current: {prediction['current_score']}")
            print(f"   Predicted: {prediction['predicted_score']}")
            print(f"   Confidence: {prediction['confidence']}%")
            print(f"   Reasoning: {prediction['reasoning']}")
        else:
            print(f"❌ Could not generate prediction: {prediction}")
        
        return True
    
    else:
        print("❌ No matches found - this is unexpected since Flashscore was working")
        return False

def test_bet9ja_option():
    """Test Bet9ja option (might not work due to connectivity)"""
    print(f"\n🇳🇬 Testing Bet9ja Option...")
    print("-" * 40)
    
    system = RealTimeSportsSystem()
    
    # Test Bet9ja URLs
    bet9ja_urls = [
        'https://sports.bet9ja.com/mobile/liveBetting',
        'https://sports.bet9ja.com/mobile/sport/1'
    ]
    
    for url in bet9ja_urls:
        print(f"🔍 Testing: {url}")
        matches = system.scrape_live_scores(url, ['Rivers United', 'Enyimba', 'Arsenal'])
        
        if matches:
            print(f"✅ Bet9ja working: Found {len(matches)} matches!")
            for match in matches[:3]:
                print(f"   ⚽ {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
            return True
        else:
            print(f"❌ No matches from {url}")
    
    print("💡 Bet9ja might be temporarily unavailable or blocking requests")
    return False

if __name__ == "__main__":
    print("🎯 Testing Complete Real-Time Sports System")
    print("=" * 70)
    
    # Test main system
    main_success = test_working_system()
    
    # Test Bet9ja option
    bet9ja_success = test_bet9ja_option()
    
    print(f"\n" + "=" * 70)
    print("📊 FINAL RESULTS:")
    print(f"✅ Main System (Flashscore): {'WORKING' if main_success else 'FAILED'}")
    print(f"🇳🇬 Bet9ja Option: {'WORKING' if bet9ja_success else 'UNAVAILABLE'}")
    
    if main_success:
        print(f"\n🎉 SYSTEM READY!")
        print("💡 You can now:")
        print("   1. Run: python start_realtime.py")
        print("   2. Open: http://localhost:3000/live-score-predictor.html")
        print("   3. Select Flashscore.com as target site")
        print("   4. Start live monitoring to see real matches!")
        
        if bet9ja_success:
            print("   5. Bet9ja is also available as an option")
        else:
            print("   5. Bet9ja option available but may need connectivity fixes")
    else:
        print(f"\n⚠️ SYSTEM NEEDS ATTENTION")
        print("💡 Check internet connection and try again")
    
    print(f"\n🚀 Test complete!")