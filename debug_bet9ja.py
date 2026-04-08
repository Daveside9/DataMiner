#!/usr/bin/env python3
"""
Debug Bet9ja Content
See what's actually on the Bet9ja pages
"""

import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def debug_bet9ja_content():
    """Debug what's on Bet9ja pages"""
    print("🇳🇬 Debugging Bet9ja Content")
    print("=" * 60)
    
    url = 'https://sports.bet9ja.com/mobile/liveBetting'
    
    try:
        # Setup Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        driver.get(url)
        time.sleep(8)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        full_text = soup.get_text()
        
        print(f"📄 Page loaded: {len(full_text)} characters")
        
        # Look for common betting/sports terms
        sports_terms = ['football', 'soccer', 'match', 'game', 'live', 'score', 'goal', 'team']
        found_terms = []
        
        for term in sports_terms:
            if term.lower() in full_text.lower():
                count = full_text.lower().count(term.lower())
                found_terms.append(f"{term}: {count}")
        
        print(f"🔍 Sports terms found: {', '.join(found_terms)}")
        
        # Look for any numbers that could be scores
        numbers = re.findall(r'\b\d+\b', full_text)
        unique_numbers = list(set(numbers))[:20]
        print(f"🔢 Numbers found: {unique_numbers}")
        
        # Look for score-like patterns
        score_patterns = [
            r'\b\d+\s*[-–:]\s*\d+\b',
            r'\b\d+\s+\d+\b',
            r'\(\d+[-–:]\d+\)',
        ]
        
        all_scores = []
        for pattern in score_patterns:
            scores = re.findall(pattern, full_text)
            if scores:
                all_scores.extend(scores[:5])
        
        if all_scores:
            print(f"⚽ Score-like patterns: {all_scores}")
        else:
            print("❌ No score patterns found")
        
        # Look for team-like words
        team_words = re.findall(r'\b[A-Z][a-zA-Z]{3,15}\b', full_text)
        unique_teams = list(set(team_words))[:20]
        print(f"🏆 Potential team names: {unique_teams}")
        
        # Look for Nigerian teams specifically
        nigerian_teams = ['Rivers', 'Enyimba', 'Kano', 'Plateau', 'Akwa', 'Lobi', 'Heartland']
        found_nigerian = []
        
        for team in nigerian_teams:
            if team.lower() in full_text.lower():
                found_nigerian.append(team)
        
        if found_nigerian:
            print(f"🇳🇬 Nigerian teams found: {found_nigerian}")
        else:
            print("❌ No Nigerian teams found")
        
        # Look for live indicators
        live_indicators = ['LIVE', 'Live', "'", 'min', 'HT', 'FT', '1H', '2H']
        found_live = []
        
        for indicator in live_indicators:
            if indicator in full_text:
                count = full_text.count(indicator)
                found_live.append(f"{indicator}: {count}")
        
        if found_live:
            print(f"🔴 Live indicators: {', '.join(found_live)}")
        else:
            print("❌ No live indicators found")
        
        # Sample some actual content
        print(f"\n📝 Sample content (first 500 chars):")
        print(full_text[:500])
        
        print(f"\n📝 Sample content (middle 500 chars):")
        mid_point = len(full_text) // 2
        print(full_text[mid_point:mid_point+500])
        
        # Look for specific elements that might contain matches
        print(f"\n🔍 Looking for match-related elements...")
        
        # Common betting site selectors
        selectors_to_try = [
            '[class*="match"]',
            '[class*="game"]', 
            '[class*="event"]',
            '[class*="live"]',
            '[class*="score"]',
            '[class*="team"]',
            'tr', 'td',  # Table elements
            '.row', '.col',  # Grid elements
        ]
        
        for selector in selectors_to_try:
            elements = soup.select(selector)
            if elements:
                print(f"   {selector}: {len(elements)} elements")
                
                # Sample first few elements
                for i, elem in enumerate(elements[:3]):
                    text = elem.get_text(strip=True)
                    if text and len(text) > 10 and len(text) < 100:
                        print(f"      Sample {i+1}: {text[:80]}...")
        
        driver.quit()
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        try:
            driver.quit()
        except:
            pass

def debug_basic_request():
    """Debug basic HTTP request to Bet9ja"""
    print(f"\n📄 Basic HTTP Request Debug")
    print("-" * 40)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get('https://sports.bet9ja.com/mobile/liveBetting', 
                              headers=headers, timeout=15)
        
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        
        if response.status_code == 200:
            # Look for any obvious content
            text = response.text.lower()
            
            if 'football' in text:
                print("✅ Contains 'football'")
            if 'live' in text:
                print("✅ Contains 'live'")
            if 'match' in text:
                print("✅ Contains 'match'")
            if 'score' in text:
                print("✅ Contains 'score'")
            
            # Sample content
            print(f"Sample: {response.text[:200]}")
        
    except Exception as e:
        print(f"❌ Basic request error: {e}")

if __name__ == "__main__":
    debug_bet9ja_content()
    debug_basic_request()