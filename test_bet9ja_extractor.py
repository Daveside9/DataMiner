#!/usr/bin/env python3
"""
Test Bet9ja History Extractor
Test the extractor with the user's specific URL
"""

import requests
import json
from datetime import datetime

def test_bet9ja_api():
    """Test the Bet9ja extractor via the data mining bot API"""
    print("🇳🇬 Testing Bet9ja History Extractor via API")
    print("=" * 60)
    
    # The URL provided by the user
    test_url = "https://sports.bet9ja.com/mobile/eventdetail/zoomsoccer/premier-zoom/premier-zoom/z.crystalpalace-z.manunited/717892344/VS_1X2"
    
    print(f"🔍 Testing URL: {test_url}")
    print(f"📊 Teams detected: Crystal Palace vs Man United")
    
    try:
        # Call the data mining bot API
        response = requests.post('http://localhost:5003/api/extract-bet9ja-history', 
                               json={'url': test_url},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            
            if result.get('success'):
                data = result.get('data', {})
                
                print(f"\n📊 Extraction Results:")
                print(f"   🏠 Home Team: {data.get('teams', {}).get('home_team', 'Unknown')}")
                print(f"   🏃 Away Team: {data.get('teams', {}).get('away_team', 'Unknown')}")
                print(f"   ⚽ Live Score: {data.get('live_score', 'No score available')}")
                print(f"   💰 Odds Found: {len(data.get('current_odds', {}))}")
                print(f"   📈 Historical Matches: {len(data.get('historical_matches', []))}")
                
                # Show some odds
                odds = data.get('current_odds', {})
                if odds:
                    print(f"\n💰 Sample Odds:")
                    for market, odd_value in list(odds.items())[:3]:
                        print(f"   {market[:30]}: {odd_value}")
                
                # Show historical matches
                historical = data.get('historical_matches', [])
                if historical:
                    print(f"\n📊 Historical Matches:")
                    for match in historical[:3]:
                        print(f"   {match.get('team', 'Team')}: {match.get('score1', 0)}-{match.get('score2', 0)} ({match.get('date', 'Unknown date')})")
                
                return True
            else:
                print(f"❌ Extraction failed: {result.get('error', 'Unknown error')}")
                return False
        
        else:
            print(f"❌ API call failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to data mining bot API")
        print("💡 Make sure the sports data mining bot is running on port 5003")
        return False
    
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_direct_extractor():
    """Test the extractor directly (fallback)"""
    print("\n🔧 Testing Direct Extractor (Fallback)")
    print("=" * 60)
    
    try:
        from bet9ja_history_extractor import Bet9jaHistoryExtractor
        
        extractor = Bet9jaHistoryExtractor()
        test_url = "https://sports.bet9ja.com/mobile/eventdetail/zoomsoccer/premier-zoom/premier-zoom/z.crystalpalace-z.manunited/717892344/VS_1X2"
        
        result = extractor.extract_match_history_from_url(test_url)
        
        if result:
            print("✅ Direct extraction successful!")
            print(f"📊 Teams: {result['teams']}")
            print(f"⚽ Live Score: {result['live_score']}")
            print(f"💰 Odds Found: {len(result['current_odds'])}")
            return True
        else:
            print("❌ Direct extraction failed")
            return False
    
    except ImportError:
        print("❌ bet9ja_history_extractor module not found")
        return False
    except Exception as e:
        print(f"❌ Direct test error: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 Bet9ja History Extractor Test Suite")
    print("=" * 60)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: API call
    api_success = test_bet9ja_api()
    
    # Test 2: Direct extractor (if API fails)
    if not api_success:
        direct_success = test_direct_extractor()
    else:
        direct_success = True
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ API Test: {'PASSED' if api_success else 'FAILED'}")
    print(f"✅ Direct Test: {'PASSED' if direct_success else 'FAILED'}")
    
    if api_success or direct_success:
        print("\n🎉 Bet9ja extractor is working!")
        print("💡 You can now extract history from Bet9ja URLs")
        print("\n📝 Usage:")
        print("   1. Use the Sports page in your frontend")
        print("   2. Select 'Bet9ja' as data source")
        print("   3. Paste your Bet9ja URL")
        print("   4. Click 'Extract History'")
    else:
        print("\n❌ Bet9ja extractor needs troubleshooting")
        print("💡 Check if:")
        print("   - Sports data mining bot is running (port 5003)")
        print("   - Internet connection is available")
        print("   - Selenium/Chrome is properly installed")

if __name__ == "__main__":
    main()