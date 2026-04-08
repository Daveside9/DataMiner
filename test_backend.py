#!/usr/bin/env python3
"""
Test Backend Connectivity and Scraping
"""

import requests
import json
from datetime import datetime

def test_backend_health():
    """Test if backend is running"""
    print("🔍 Testing Backend Health...")
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Backend is healthy!")
            print(f"   Status: {result['status']}")
            print(f"   Timestamp: {result['timestamp']}")
            return True
        else:
            print(f"❌ Backend returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running")
        print("   Please start: python backend/app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_scraping_endpoint():
    """Test the scraping endpoint with simple data"""
    print("\n🧪 Testing Scraping Endpoint...")
    
    test_data = {
        "url": "https://quotes.toscrape.com",  # Simple test site
        "selectors": {
            "quotes": ".quote .text",
            "authors": ".quote .author",
            "tags": ".quote .tags"
        }
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/scrape',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Scraping endpoint works!")
                data = result['data']['data']
                for key, values in data.items():
                    print(f"   {key}: {len(values)} items found")
                    if values:
                        print(f"      Sample: {values[0][:50]}...")
                return True
            else:
                print(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Scraping test error: {e}")
        return False

def test_sports_scraping():
    """Test scraping with sports-like selectors"""
    print("\n⚽ Testing Sports Scraping...")
    
    # Test with BBC Sport (should be accessible)
    test_data = {
        "url": "https://www.bbc.com/sport/football",
        "selectors": {
            "teams": ".sp-c-fixture__team-name, .team-name, .home, .away",
            "dates": ".sp-c-fixture__date, .date, .time",
            "scores": ".sp-c-fixture__score, .score"
        }
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/scrape',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Sports scraping works!")
                data = result['data']['data']
                for key, values in data.items():
                    print(f"   {key}: {len(values)} items found")
                    if values:
                        print(f"      Sample: {values[0][:50]}...")
                return True
            else:
                print(f"❌ Sports scraping failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Sports scraping error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 DataMiner Backend Test Suite")
    print("=" * 50)
    
    # Test 1: Backend Health
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start it first:")
        print("   cd my-portfolio/DataMiner")
        print("   python backend/app.py")
        return
    
    # Test 2: Basic Scraping
    if not test_scraping_endpoint():
        print("\n❌ Basic scraping failed")
        return
    
    # Test 3: Sports Scraping
    test_sports_scraping()
    
    print("\n" + "=" * 50)
    print("🎉 Backend tests completed!")
    print("💡 If all tests passed, your scraper should work")
    print("🌐 Open: http://localhost:3000/historical-pattern-scraper.html")

if __name__ == "__main__":
    main()