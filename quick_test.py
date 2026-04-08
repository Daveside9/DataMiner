#!/usr/bin/env python3
"""
Quick test script to demonstrate DataMiner usage
"""

import requests
import json

# Test the scraper
def test_scrape():
    url = "http://localhost:5000/api/scrape"
    
    # Example 1: Basic scraping
    data = {
        "url": "https://httpbin.org/html",
        "selectors": {
            "title": "title",
            "headings": "h1",
            "paragraphs": "p"
        }
    }
    
    print("🕷️ Testing DataMiner...")
    print(f"📡 Scraping: {data['url']}")
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("✅ Scraping successful!")
            print(f"📊 Method: {result['data']['method']}")
            print(f"🕐 Time: {result['timestamp']}")
            print("\n📋 Extracted Data:")
            
            scraped_data = result['data']['data']
            for key, value in scraped_data.items():
                if isinstance(value, list):
                    print(f"  {key}: {len(value)} items")
                    if value:
                        print(f"    Sample: {str(value[0])[:100]}...")
                else:
                    print(f"  {key}: {str(value)[:100]}...")
        else:
            print(f"❌ Scraping failed: {result.get('error')}")
    else:
        print(f"❌ Request failed: {response.status_code}")

if __name__ == "__main__":
    test_scrape()