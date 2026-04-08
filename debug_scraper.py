#!/usr/bin/env python3
"""
Debug Scraper - Find exactly what's on the page
"""

import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def debug_page_content(url):
    """Debug what's actually on the page"""
    print(f"🔍 Debugging page content: {url}")
    print("=" * 60)
    
    # Method 1: Basic requests
    print("📄 METHOD 1: Basic HTML Content")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        print(f"   Status: {response.status_code}")
        print(f"   Content length: {len(text)} characters")
        
        # Look for ANY numbers that could be scores
        numbers = re.findall(r'\d+', text)
        print(f"   All numbers found: {numbers[:20]}...")
        
        # Look for score-like patterns
        score_patterns = [
            r'\d+\s*[-–—:]\s*\d+',
            r'\d+\s+\d+',
            r'\(\d+[-–]\d+\)',
        ]
        
        for pattern in score_patterns:
            matches = re.findall(pattern, text)
            if matches:
                print(f"   Pattern '{pattern}': {matches[:5]}")
        
        # Look for team-like words
        team_words = re.findall(r'\b[A-Z][a-z]{3,}\b', text)
        print(f"   Potential teams: {team_words[:10]}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    
    # Method 2: Selenium with JavaScript
    print("🌐 METHOD 2: Selenium with JavaScript")
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        driver.get(url)
        time.sleep(5)  # Wait for JavaScript to load
        
        # Get page source after JavaScript execution
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        text = soup.get_text()
        
        print(f"   Page loaded with JS: {len(text)} characters")
        
        # Look for live indicators
        live_indicators = ['LIVE', 'Live', "'", '+', 'min', 'HT', 'FT']
        found_live = []
        for indicator in live_indicators:
            if indicator in text:
                found_live.append(indicator)
        
        if found_live:
            print(f"   Live indicators found: {found_live}")
        
        # Look for score patterns again
        score_patterns = [
            r'\d+\s*[-–—:]\s*\d+',
            r'\d+\s+\d+',
            r'\(\d+[-–]\d+\)',
        ]
        
        for pattern in score_patterns:
            matches = re.findall(pattern, text)
            if matches:
                print(f"   JS Pattern '{pattern}': {matches[:5]}")
        
        # Look for specific elements that might contain scores
        score_elements = driver.find_elements("css selector", "[class*='score'], [class*='result'], [class*='match']")
        print(f"   Score-related elements: {len(score_elements)}")
        
        for i, elem in enumerate(score_elements[:5]):
            try:
                elem_text = elem.text.strip()
                if elem_text and len(elem_text) < 50:
                    print(f"      Element {i+1}: '{elem_text}'")
            except:
                continue
        
        driver.quit()
        
    except Exception as e:
        print(f"   ❌ Selenium error: {e}")
    
    print("\n" + "=" * 60)
    print("💡 Analysis complete!")

if __name__ == "__main__":
    # Test with the URL that has live matches
    test_urls = [
        'https://www.livescore.com/en/football/',
        'https://www.flashscore.com/football/',
        'https://www.bbc.com/sport/football/scores-fixtures'
    ]
    
    for url in test_urls:
        debug_page_content(url)
        print("\n" + "="*80 + "\n")