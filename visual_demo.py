#!/usr/bin/env python3
"""
Visual Demo - Test the visual inspection capabilities
"""

import requests
import json
import webbrowser
import time

API_BASE = "http://localhost:5000/api"

def test_site_analyzer():
    """Test the site structure analyzer"""
    print("🔍 VISUAL SITE ANALYSIS DEMO")
    print("=" * 50)
    
    test_sites = [
        "https://www.bbc.com/sport/football/scores-fixtures",
        "https://quotes.toscrape.com/",
        "https://news.ycombinator.com/"
    ]
    
    for url in test_sites:
        print(f"\n📡 Analyzing: {url}")
        
        try:
            response = requests.post(f"{API_BASE}/analyze-site", json={"url": url})
            
            if response.status_code == 200:
                analysis = response.json()["analysis"]
                
                if "error" in analysis:
                    print(f"❌ Error: {analysis['error']}")
                    continue
                
                print(f"✅ Analysis complete!")
                print(f"📄 Title: {analysis['title']}")
                print(f"📊 Total elements: {analysis['structure']['total_elements']}")
                
                # Show top suggested selectors
                print(f"\n🎯 TOP SELECTOR SUGGESTIONS:")
                for category, suggestions in analysis['suggested_selectors'].items():
                    if suggestions:
                        print(f"  {category.upper()}:")
                        for suggestion in suggestions[:1]:  # Show top 1
                            print(f"    • {suggestion['selector']}")
                            print(f"      Found: {suggestion['count']} elements")
                            print(f"      Sample: {suggestion['sample_text'][:60]}...")
                
                # Show data elements
                data_elements = analysis.get('data_elements', [])
                if data_elements:
                    print(f"\n📊 DETECTED DATA ELEMENTS:")
                    for elem in data_elements[:5]:  # Show top 5
                        print(f"    • {elem['selector']} ({elem['likely_data_type']})")
                        print(f"      Text: {elem['text']}")
                
            else:
                print(f"❌ API request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)  # Brief pause between requests

def open_visual_interfaces():
    """Open all visual interfaces"""
    print(f"\n🌐 OPENING VISUAL INTERFACES")
    print("=" * 40)
    
    interfaces = [
        ("Main Scraper", "http://localhost:8080/"),
        ("Visual Inspector", "http://localhost:8080/visual-inspector.html"),
        ("Sports Dashboard", "http://localhost:8080/sports-dashboard.html"),
        ("Analysis Dashboard", "http://localhost:8080/analysis.html")
    ]
    
    for name, url in interfaces:
        print(f"🔗 Opening {name}: {url}")
        try:
            webbrowser.open(url)
            time.sleep(2)  # Delay between opening tabs
        except Exception as e:
            print(f"⚠️ Could not open {name}: {e}")

def demo_visual_scraping():
    """Demo visual scraping with a test site"""
    print(f"\n🎯 VISUAL SCRAPING DEMO")
    print("=" * 30)
    
    # Test with quotes site (reliable structure)
    test_url = "https://quotes.toscrape.com/"
    selectors = {
        "quotes": ".quote .text",
        "authors": ".quote .author", 
        "tags": ".quote .tags a"
    }
    
    print(f"📡 Testing visual scraping on: {test_url}")
    print(f"🎯 Using selectors: {list(selectors.keys())}")
    
    try:
        response = requests.post(f"{API_BASE}/scrape", json={
            "url": test_url,
            "selectors": selectors
        })
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print(f"✅ Visual scraping successful!")
                
                data = result['data']['data']
                print(f"\n📊 SCRAPED DATA PREVIEW:")
                
                for key, value in data.items():
                    if isinstance(value, list) and value:
                        print(f"\n{key.upper()} ({len(value)} items):")
                        for i, item in enumerate(value[:3], 1):
                            print(f"  {i}. {item[:80]}{'...' if len(item) > 80 else ''}")
                        if len(value) > 3:
                            print(f"  ... and {len(value) - 3} more")
                    elif value:
                        print(f"\n{key.upper()}: {value}")
                
                print(f"\n💡 This data would be displayed visually in the interface!")
                
            else:
                print(f"❌ Scraping failed: {result.get('error')}")
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Demo error: {e}")

def main():
    """Run the complete visual demo"""
    print("🎨 DATAMINER VISUAL DEMO")
    print("🔍 Visual Site Inspection & Analysis")
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
    
    # Run demos
    test_site_analyzer()
    demo_visual_scraping()
    
    print(f"\n" + "=" * 60)
    print("🎉 VISUAL DEMO COMPLETE!")
    
    print(f"\n🌐 YOUR VISUAL INTERFACES:")
    print("  • Main Interface: http://localhost:8080/")
    print("  • Visual Inspector: http://localhost:8080/visual-inspector.html")
    print("  • Sports Dashboard: http://localhost:8080/sports-dashboard.html")
    print("  • Analysis Dashboard: http://localhost:8080/analysis.html")
    
    print(f"\n💡 WHAT YOU CAN DO:")
    print("  1. 🔍 Load any website in Visual Inspector")
    print("  2. 🎯 See suggested CSS selectors automatically")
    print("  3. 📊 Test selectors and see live results")
    print("  4. 📈 View scraped data with visual charts")
    print("  5. ⚽ Use Sports Dashboard for match data")
    print("  6. 🕐 Set up automated data collection")
    
    # Ask if user wants to open interfaces
    try:
        choice = input(f"\n🚀 Open all visual interfaces now? (y/n): ").lower()
        if choice == 'y':
            open_visual_interfaces()
    except:
        pass

if __name__ == "__main__":
    main()