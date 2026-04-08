#!/usr/bin/env python3
"""
Live Demo of DataMiner capabilities
"""

import requests
import json
import time

API_BASE = "http://localhost:5000/api"

def demo_basic_scraping():
    """Demo 1: Basic website scraping"""
    print("🎯 DEMO 1: Basic Website Scraping")
    print("=" * 50)
    
    # Test with a reliable site
    data = {
        "url": "https://quotes.toscrape.com/",
        "selectors": {
            "quotes": ".quote .text",
            "authors": ".quote .author",
            "tags": ".quote .tags a"
        }
    }
    
    print(f"📡 Scraping: {data['url']}")
    print("🎯 Looking for: quotes, authors, tags")
    
    response = requests.post(f"{API_BASE}/scrape", json=data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("✅ SUCCESS!")
            scraped_data = result['data']['data']
            
            for key, value in scraped_data.items():
                if isinstance(value, list) and value:
                    print(f"📋 {key}: Found {len(value)} items")
                    print(f"   Sample: {value[0][:100]}...")
                elif value:
                    print(f"📋 {key}: {str(value)[:100]}...")
            
            return result
        else:
            print(f"❌ Failed: {result.get('error')}")
    else:
        print(f"❌ Request failed: {response.status_code}")
    
    return None

def demo_news_scraping():
    """Demo 2: News website scraping"""
    print("\n🎯 DEMO 2: News Website Scraping")
    print("=" * 50)
    
    data = {
        "url": "https://news.ycombinator.com/",
        "selectors": {
            "titles": ".titleline > a",
            "scores": ".score",
            "comments": ".subline a[href*='item']"
        }
    }
    
    print(f"📡 Scraping: {data['url']}")
    print("🎯 Looking for: titles, scores, comments")
    
    response = requests.post(f"{API_BASE}/scrape", json=data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("✅ SUCCESS!")
            scraped_data = result['data']['data']
            
            for key, value in scraped_data.items():
                if isinstance(value, list) and value:
                    print(f"📋 {key}: Found {len(value)} items")
                    if key == "titles":
                        print(f"   Top story: {value[0][:80]}...")
                elif value:
                    print(f"📋 {key}: {str(value)[:100]}...")
            
            return result
        else:
            print(f"❌ Failed: {result.get('error')}")
    else:
        print(f"❌ Request failed: {response.status_code}")
    
    return None

def demo_pattern_analysis():
    """Demo 3: Pattern analysis"""
    print("\n🎯 DEMO 3: Pattern Analysis")
    print("=" * 50)
    
    # First, let's see what data sources we have
    response = requests.get(f"{API_BASE}/sources")
    
    if response.status_code == 200:
        sources = response.json().get("sources", [])
        print(f"📊 Found {len(sources)} data sources:")
        
        for source in sources:
            print(f"  • {source['name']}: {source['total_scrapes']} scrapes")
            
            if source['total_scrapes'] > 0:
                print(f"    Analyzing patterns for {source['name']}...")
                
                # Analyze this source
                analysis_response = requests.get(f"{API_BASE}/analyze/{source['name']}")
                
                if analysis_response.status_code == 200:
                    analysis = analysis_response.json().get("analysis", {})
                    
                    print("    ✅ Analysis complete!")
                    
                    # Show insights
                    insights = analysis.get("insights", [])
                    if insights:
                        print("    💡 Key Insights:")
                        for insight in insights[:3]:  # Show first 3 insights
                            print(f"      - {insight}")
                    
                    # Show summary stats
                    summary = analysis.get("summary", {})
                    if summary:
                        print(f"    📈 Total records: {summary.get('total_records', 0)}")
                        print(f"    📈 Success rate: {summary.get('success_rate', 0):.1%}")
                else:
                    print("    ❌ Analysis failed")
    else:
        print("❌ Could not fetch data sources")

def demo_historical_collection():
    """Demo 4: Historical data collection"""
    print("\n🎯 DEMO 4: Historical Data Collection")
    print("=" * 50)
    
    print("🕐 Collecting data at 30-second intervals (3 samples)...")
    
    urls_to_test = [
        "https://httpbin.org/json",
        "https://httpbin.org/html",
        "https://httpbin.org/user-agent"
    ]
    
    for i, url in enumerate(urls_to_test):
        print(f"\n📡 Collection {i+1}/3: {url}")
        
        data = {"url": url, "selectors": {}}
        response = requests.post(f"{API_BASE}/scrape", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Sample {i+1} collected successfully")
                data_size = len(str(result['data']))
                print(f"📊 Data size: {data_size} characters")
            else:
                print(f"❌ Sample {i+1} failed")
        
        if i < len(urls_to_test) - 1:
            print("⏳ Waiting 5 seconds...")
            time.sleep(5)
    
    print("\n🎯 Historical collection complete!")

def main():
    """Run all demos"""
    print("🚀 DataMiner Live Demonstration")
    print("🔍 Universal Web Scraping & Pattern Analysis")
    print("=" * 60)
    
    # Check API health
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ API Server is running")
        else:
            print("❌ API Server not responding")
            return
    except:
        print("❌ Cannot connect to API server")
        return
    
    # Run demos
    demos = [
        demo_basic_scraping,
        demo_news_scraping,
        demo_historical_collection,
        demo_pattern_analysis
    ]
    
    for demo in demos:
        try:
            demo()
            time.sleep(2)  # Brief pause between demos
        except Exception as e:
            print(f"❌ Demo failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Demo Complete!")
    print("\n🌐 Access your DataMiner:")
    print("  • Web Interface: http://localhost:8080")
    print("  • Analysis Dashboard: http://localhost:8080/analysis.html")
    print("  • API Docs: http://localhost:5000/api/health")
    
    print("\n💡 What you can do next:")
    print("  1. Try scraping your favorite websites")
    print("  2. Set up automated data collection")
    print("  3. Analyze patterns in your collected data")
    print("  4. Export data for further analysis")

if __name__ == "__main__":
    main()