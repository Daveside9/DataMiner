#!/usr/bin/env python3
"""
Direct API Test for Bet9ja
"""

import requests
import json

def test_api_direct():
    url = "https://sports.bet9ja.com/mobile/eventdetail/zoomsoccer/premier-zoom/premier-zoom/z.crystalpalace-z.manunited/717892344/VS_1X2"
    
    try:
        response = requests.post('http://localhost:5003/api/extract-bet9ja-history', 
                               json={'url': url},
                               timeout=60)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON Response: {json.dumps(data, indent=2)}")
            except:
                print("Response is not valid JSON")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_direct()