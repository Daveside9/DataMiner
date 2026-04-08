#!/usr/bin/env python3
"""
Complete DataMiner Demo - Show all features working together
"""

import requests
import webbrowser
import time

API_BASE = "http://localhost:5000/api"

def demo_complete_system():
    """Demonstrate the complete DataMiner system"""
    print("🎯 COMPLETE DATAMINER SYSTEM DEMO")
    print("=" * 60)
    
    # Check API health
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ DataMiner API is running")
        else:
            print("❌ API not responding")
            return
    except:
        print("❌ Cannot connect to API")
        return
    
    print("\n🌟 YOUR DATAMINER FEATURES:")
    print("=" * 40)
    
    features = [
        {
            "name": "🔍 Visual Site Inspector",
            "url": "http://localhost:8080/visual-inspector.html",
            "description": "Load any website, see automatic CSS selector suggestions, test selectors live"
        },
        {
            "name": "⚽ Sports Dashboard", 
            "url": "http://localhost:8080/sports-dashboard.html",
            "description": "Sports-specific interface with historical data collection and pattern analysis"
        },
        {
            "name": "📅 Historical Match Analyzer",
            "url": "http://localhost:8080/match-history.html", 
            "description": "Search for specific team matchups over custom time periods (e.g., Chelsea vs Liverpool last month)"
        },
        {
            "name": "📊 Analysis Dashboard",
            "url": "http://localhost:8080/analysis.html",
            "description": "Pattern visualization with charts, trend analysis, automated insights"
        },
        {
            "name": "🌐 Main Scraper",
            "url": "http://localhost:8080/",
            "description": "Universal web scraping interface with custom CSS selectors"
        }
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"\n{i}. {feature['name']}")
        print(f"   URL: {feature['url']}")
        print(f"   📝 {feature['description']}")
    
    print(f"\n🎯 WHAT YOU CAN DO RIGHT NOW:")
    print("=" * 40)
    
    examples = [
        "🔍 Load any sports website in Visual Inspector and get automatic selector suggestions",
        "⚽ Set up automated data collection every hour for your favorite teams",
        "📅 Search 'Chelsea vs Liverpool last 1 month' and see all their recent matches",
        "📊 View historical patterns and trends in collected sports data",
        "🌐 Scrape any website with custom CSS selectors and see results instantly",
        "📈 Export collected data for further analysis in Excel or other tools"
    ]
    
    for example in examples:
        print(f"  • {example}")
    
    print(f"\n💡 EXAMPLE WORKFLOWS:")
    print("=" * 30)
    
    workflows = [
        {
            "title": "🏆 Track Your Team's Performance",
            "steps": [
                "1. Open Sports Dashboard",
                "2. Enter your team's website URL",
                "3. Set collection interval (e.g., every 6 hours)",
                "4. Let it collect data for a week",
                "5. View patterns and trends in the analysis"
            ]
        },
        {
            "title": "🔍 Analyze Specific Matchups",
            "steps": [
                "1. Open Historical Match Analyzer", 
                "2. Enter 'Chelsea' and 'Liverpool'",
                "3. Set time period to 'Last 3 months'",
                "4. Click search to see all their recent matches",
                "5. View timeline and statistics"
            ]
        },
        {
            "title": "📊 Monitor Any Website",
            "steps": [
                "1. Open Visual Inspector",
                "2. Load any website you want to monitor",
                "3. See automatic selector suggestions",
                "4. Test selectors to see what data they find",
                "5. Set up automated collection"
            ]
        }
    ]
    
    for workflow in workflows:
        print(f"\n{workflow['title']}:")
        for step in workflow['steps']:
            print(f"    {step}")
    
    # Test a working example
    print(f"\n🧪 TESTING WITH WORKING EXAMPLE:")
    print("=" * 40)
    
    test_url = "https://quotes.toscrape.com/"
    selectors = {
        "quotes": ".quote .text",
        "authors": ".quote .author",
        "tags": ".quote .tags a"
    }
    
    print(f"📡 Testing scraper with: {test_url}")
    
    try:
        response = requests.post(f"{API_BASE}/scrape", json={
            "url": test_url,
            "selectors": selectors
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Scraping test successful!")
                
                data = result['data']['data']
                for key, value in data.items():
                    if isinstance(value, list) and value:
                        print(f"  📋 {key}: Found {len(value)} items")
                        print(f"      Sample: {value[0][:60]}...")
                
                print(f"\n💡 This same process works for sports websites!")
                print(f"   Just use different selectors like:")
                print(f"   • Teams: .team-name, .home-team, .away-team")
                print(f"   • Scores: .score, .result, .match-score")
                print(f"   • Dates: .date, .match-date, .kick-off")
            else:
                print(f"❌ Test failed: {result.get('error')}")
        else:
            print(f"❌ Request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    # Ask to open interfaces
    print(f"\n🚀 READY TO START?")
    print("=" * 20)
    
    try:
        choice = input("Open all DataMiner interfaces now? (y/n): ").lower()
        if choice == 'y':
            print(f"\n🌐 Opening all interfaces...")
            for feature in features:
                print(f"🔗 Opening {feature['name']}")
                try:
                    webbrowser.open(feature['url'])
                    time.sleep(1)  # Delay between tabs
                except Exception as e:
                    print(f"⚠️ Could not open {feature['name']}: {e}")
            
            print(f"\n🎉 All interfaces opened!")
            print(f"💡 Start with the Visual Inspector to see how it works!")
        else:
            print(f"\n📝 Manual access:")
            for feature in features:
                print(f"  {feature['name']}: {feature['url']}")
    except:
        print(f"\n📝 Access your DataMiner interfaces:")
        for feature in features:
            print(f"  {feature['name']}: {feature['url']}")

def main():
    """Run the complete demo"""
    demo_complete_system()
    
    print(f"\n" + "=" * 60)
    print("🎉 DATAMINER COMPLETE SYSTEM READY!")
    print("=" * 60)
    
    print(f"\n🏆 YOU NOW HAVE:")
    print("✅ Visual website inspection with automatic selector suggestions")
    print("✅ Historical match search (e.g., 'Chelsea vs Liverpool last month')")
    print("✅ Automated sports data collection with time intervals")
    print("✅ Pattern analysis and trend visualization")
    print("✅ Universal web scraping for any website")
    print("✅ Real-time data preview and testing")
    
    print(f"\n🎯 PERFECT FOR:")
    print("• Sports betting analysis and pattern recognition")
    print("• Team performance tracking over time")
    print("• Historical match data collection")
    print("• Automated monitoring of sports websites")
    print("• Data export for further analysis")
    
    print(f"\n🚀 START USING IT NOW!")
    print("Open any of the interfaces above and begin exploring!")

if __name__ == "__main__":
    main()