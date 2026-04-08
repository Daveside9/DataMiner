#!/usr/bin/env python3
"""
Test Sports Data Mining Bot
Quick test to verify the bot functionality
"""

import requests
import json
import time

def test_bot_api():
    """Test the data mining bot API"""
    base_url = "http://localhost:5003"
    
    print("🧪 Testing Sports Data Mining Bot API")
    print("=" * 50)
    
    # Test 1: Check bot status
    print("\n1. Checking bot status...")
    try:
        response = requests.get(f"{base_url}/api/bot-status")
        if response.status_code == 200:
            status = response.json()
            print("✅ Bot status retrieved:")
            print(f"   📊 Teams in database: {status['teams_in_database']}")
            print(f"   ⚽ Matches in database: {status['matches_in_database']}")
            print(f"   🔄 Mining active: {status['mining_active']}")
            print(f"   📸 Screen monitoring: {status['screen_monitoring_active']}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status check error: {e}")
    
    # Test 2: Mine Arsenal history
    print("\n2. Mining Arsenal historical data...")
    try:
        response = requests.post(f"{base_url}/api/mine-team-history", json={
            "team_name": "Arsenal",
            "analysis_period": "3_months"
        })
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Arsenal data mining successful:")
            analysis = result.get('analysis', {})
            print(f"   📊 Analysis period: {analysis.get('analysis_period', 'N/A')}")
            print(f"   ⚽ Matches found: {analysis.get('matches_found', 0)}")
            print(f"   📈 Recent form: {analysis.get('recent_form', {})}")
        else:
            print(f"❌ Arsenal mining failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Arsenal mining error: {e}")
    
    # Test 3: Start data mining for multiple teams
    print("\n3. Starting comprehensive data mining...")
    try:
        response = requests.post(f"{base_url}/api/start-data-mining", json={
            "teams": ["Chelsea", "Liverpool"],
            "time_period": "1_month",
            "sources": ["flashscore", "bbc_sport"]
        })
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Comprehensive mining started:")
            print(f"   👥 Teams: {result.get('teams', [])}")
            print(f"   ⏱️ Period: {result.get('time_period', 'N/A')}")
            
            # Wait a bit and check status
            print("   ⏳ Waiting 10 seconds...")
            time.sleep(10)
            
            status_response = requests.get(f"{base_url}/api/bot-status")
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"   📊 Updated teams count: {status['teams_in_database']}")
                print(f"   ⚽ Updated matches count: {status['matches_in_database']}")
        else:
            print(f"❌ Comprehensive mining failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Comprehensive mining error: {e}")
    
    # Test 4: Get mined data
    print("\n4. Retrieving mined data...")
    try:
        response = requests.get(f"{base_url}/api/get-mined-data?team=Arsenal")
        if response.status_code == 200:
            data = response.json()
            print("✅ Arsenal data retrieved:")
            print(f"   📊 Team: {data.get('team', 'N/A')}")
            print(f"   📅 Last updated: {data.get('last_updated', 'N/A')}")
            
            analysis = data.get('analysis', {})
            if analysis:
                print(f"   ⚽ Matches analyzed: {analysis.get('matches_found', 0)}")
                recent_form = analysis.get('recent_form', {})
                if recent_form:
                    print(f"   📈 Recent wins: {recent_form.get('wins', 0)}")
                    print(f"   📈 Recent draws: {recent_form.get('draws', 0)}")
                    print(f"   📈 Recent losses: {recent_form.get('losses', 0)}")
        else:
            print(f"❌ Data retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Data retrieval error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Bot API testing completed!")
    print("💡 If you see errors, make sure the bot is running:")
    print("   python sports_data_mining_bot.py")

def main():
    """Main test function"""
    print("🤖 Sports Data Mining Bot - API Test")
    print("=" * 50)
    
    # Check if bot is running
    try:
        response = requests.get("http://localhost:5003/api/bot-status", timeout=5)
        if response.status_code == 200:
            print("✅ Bot is running, starting tests...")
            test_bot_api()
        else:
            print("❌ Bot is not responding properly")
    except requests.exceptions.ConnectionError:
        print("❌ Bot is not running!")
        print("💡 Start the bot first:")
        print("   python sports_data_mining_bot.py")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    main()