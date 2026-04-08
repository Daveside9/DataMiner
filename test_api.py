#!/usr/bin/env python3
"""
Test the DataMiner API endpoints
"""

import requests
import json
import time

API_BASE = "http://localhost:5000/api"

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_scraping():
    """Test the scraping endpoint"""
    print("\n🕷️ Testing scraping endpoint...")
    
    # Test with a simple JSON API
    test_data = {
        "url": "https://httpbin.org/json",
        "selectors": {}
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/scrape",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Scraping test passed!")
                print(f"📊 Data size: {len(str(data['data']))} characters")
                print(f"🕐 Timestamp: {data['timestamp']}")
                return True
            else:
                print(f"❌ Scraping failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Scraping request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Scraping test error: {e}")
        return False

def test_with_selectors():
    """Test scraping with CSS selectors"""
    print("\n🎯 Testing scraping with selectors...")
    
    # Test with a website that has structured content
    test_data = {
        "url": "https://httpbin.org/html",
        "selectors": {
            "title": "title",
            "headings": "h1",
            "paragraphs": "p"
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/scrape",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Selector-based scraping test passed!")
                scraped_data = data['data']['data']
                for key, value in scraped_data.items():
                    if isinstance(value, list):
                        print(f"📋 {key}: {len(value)} items")
                    else:
                        print(f"📋 {key}: {str(value)[:50]}...")
                return True
            else:
                print(f"❌ Selector scraping failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Selector scraping request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Selector scraping test error: {e}")
        return False

def test_data_sources():
    """Test data sources endpoint"""
    print("\n📚 Testing data sources endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/sources")
        
        if response.status_code == 200:
            data = response.json()
            sources = data.get("sources", [])
            print(f"✅ Data sources test passed!")
            print(f"📊 Found {len(sources)} data sources")
            return True
        else:
            print(f"❌ Data sources request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Data sources test error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 DataMiner API Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Basic Scraping", test_scraping),
        ("Selector Scraping", test_with_selectors),
        ("Data Sources", test_data_sources)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(1)  # Small delay between tests
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 API Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} API tests passed")
    
    if passed == len(results):
        print("🎉 All API tests passed! DataMiner API is working correctly.")
        print("\n🌐 Frontend available at: file:///path/to/DataMiner/frontend/index.html")
    else:
        print("⚠️ Some API tests failed. Check the server logs.")

if __name__ == "__main__":
    main()