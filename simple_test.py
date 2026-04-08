#!/usr/bin/env python3
"""
Simple test to check what's working
"""

import requests
import json

def test_bot_status():
    """Test if bot is responding"""
    try:
        response = requests.get('http://localhost:5003/api/bot-status', timeout=5)
        print(f"Bot Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return True
    except Exception as e:
        print(f"Bot connection error: {e}")
        return False

def test_team_extraction():
    """Test team name extraction"""
    try:
        from advanced_team_analyzer import AdvancedTeamAnalyzer
        
        analyzer = AdvancedTeamAnalyzer()
        url = "https://sports.bet9ja.com/mobile/eventdetail/zoomsoccer/premier-zoom/premier-zoom/z.crystalpalace-z.manunited/717892344/VS_1X2"
        
        teams = analyzer.extract_teams_from_url(url)
        print(f"Extracted teams: {teams}")
        
        # Test team name cleaning
        test_names = ['crystalpalace', 'manunited', 'z.crystalpalace', 'z.manunited']
        for name in test_names:
            clean_name = analyzer.clean_team_name(name)
            print(f"'{name}' -> '{clean_name}'")
        
        return True
    except Exception as e:
        print(f"Team extraction error: {e}")
        return False

def test_simple_api():
    """Test simple API call"""
    try:
        url = "https://sports.bet9ja.com/mobile/eventdetail/zoomsoccer/premier-zoom/premier-zoom/z.crystalpalace-z.manunited/717892344/VS_1X2"
        
        response = requests.post('http://localhost:5003/api/extract-bet9ja-history', 
                               json={'url': url},
                               timeout=30)
        
        print(f"API Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Teams found: {result.get('teams_found', {})}")
            return True
        else:
            print(f"API Error: {response.text}")
            return False
    except Exception as e:
        print(f"API test error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Simple Diagnostic Test")
    print("=" * 40)
    
    print("\n1. Testing bot connection...")
    bot_ok = test_bot_status()
    
    print("\n2. Testing team extraction...")
    extraction_ok = test_team_extraction()
    
    print("\n3. Testing API call...")
    api_ok = test_simple_api()
    
    print("\n" + "=" * 40)
    print("RESULTS:")
    print(f"✅ Bot Connection: {'OK' if bot_ok else 'FAILED'}")
    print(f"✅ Team Extraction: {'OK' if extraction_ok else 'FAILED'}")
    print(f"✅ API Call: {'OK' if api_ok else 'FAILED'}")