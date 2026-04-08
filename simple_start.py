#!/usr/bin/env python3
"""
SIMPLE START - Just the basics you need
"""

import requests
import webbrowser

def simple_demo():
    """Show the simplest way to use DataMiner"""
    print("🎯 SIMPLE DATAMINER - EASY START")
    print("=" * 40)
    
    print("✅ What you have:")
    print("  1. A web scraper that works")
    print("  2. A visual interface to use it")
    print("  3. Ability to get sports data")
    
    print(f"\n🚀 EASIEST WAY TO START:")
    print("=" * 30)
    
    print("STEP 1: Open your browser")
    print("STEP 2: Go to: http://localhost:8080")
    print("STEP 3: Enter a website URL")
    print("STEP 4: Click 'Start Scraping'")
    print("STEP 5: See the data!")
    
    print(f"\n💡 EXAMPLE:")
    print("URL: https://quotes.toscrape.com")
    print("Result: You'll see quotes, authors, tags")
    
    print(f"\n⚽ FOR SPORTS:")
    print("URL: Any sports website")
    print("Result: Team names, scores, dates")
    
    # Test if API is running
    try:
        response = requests.get("http://localhost:5000/api/health")
        if response.status_code == 200:
            print(f"\n✅ Your DataMiner is READY!")
            
            choice = input(f"\nOpen the simple interface now? (y/n): ")
            if choice.lower() == 'y':
                webbrowser.open("http://localhost:8080")
                print("🌐 Interface opened! Try scraping a website!")
        else:
            print(f"\n❌ DataMiner not running")
            print("Run: python backend/app.py")
    except:
        print(f"\n❌ DataMiner not running")
        print("Run: python backend/app.py")

if __name__ == "__main__":
    simple_demo()