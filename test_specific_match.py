#!/usr/bin/env python3
"""
Test Specific Match Detection
Look for the exact pattern we saw in debug: "Japan U23 Syria U23 5 0"
"""

import sys
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def test_flashscore_specific():
    """Test Flashscore for the specific match we saw"""
    print("🔍 Testing Flashscore for specific match pattern...")
    
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
        
        driver.get('https://www.flashscore.com/football/')
        time.sleep(5)
        
        # Get all text content
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        full_text = soup.get_text()
        
        print(f"📄 Page loaded: {len(full_text)} characters")
        
        # Look for the specific pattern we saw: "Japan U23 Syria U23 5 0"
        if "Japan U23" in full_text and "Syria U23" in full_text:
            print("✅ Found Japan U23 vs Syria U23 match!")
            
            # Extract the context around this match
            japan_index = full_text.find("Japan U23")
            if japan_index != -1:
                context_start = max(0, japan_index - 100)
                context_end = min(len(full_text), japan_index + 200)
                context = full_text[context_start:context_end]
                
                print("📝 Context around match:")
                print(context)
                print("-" * 40)
                
                # Look for score patterns in this context
                score_patterns = [
                    r'Japan U23\s*Syria U23\s*(\d+)\s*(\d+)',
                    r'Japan U23.*?Syria U23.*?(\d+).*?(\d+)',
                    r'(\d+)\s*(\d+).*?Japan U23.*?Syria U23',
                    r'Japan U23\s*(\d+)\s*Syria U23\s*(\d+)',
                ]
                
                for pattern in score_patterns:
                    matches = re.findall(pattern, context, re.DOTALL | re.IGNORECASE)
                    if matches:
                        print(f"🎯 Pattern '{pattern}' found: {matches}")
                        for match in matches:
                            if len(match) == 2:
                                score1, score2 = match
                                try:
                                    s1, s2 = int(score1), int(score2)
                                    if 0 <= s1 <= 20 and 0 <= s2 <= 20:
                                        print(f"⚽ MATCH FOUND: Japan U23 {s1}-{s2} Syria U23")
                                        return True
                                except ValueError:
                                    continue
        
        # Look for any team-score patterns
        print("\n🔍 Looking for any team-score patterns...")
        
        # Pattern: Team1 Team2 Number Number
        team_score_pattern = r'([A-Z][a-zA-Z\s]+?U23)\s+([A-Z][a-zA-Z\s]+?U23)\s+(\d+)\s+(\d+)'
        matches = re.findall(team_score_pattern, full_text)
        
        if matches:
            print(f"🎯 Found {len(matches)} potential U23 matches:")
            for i, match in enumerate(matches[:5]):
                team1, team2, score1, score2 = match
                try:
                    s1, s2 = int(score1), int(score2)
                    if 0 <= s1 <= 20 and 0 <= s2 <= 20:
                        print(f"   {i+1}. {team1.strip()} {s1}-{s2} {team2.strip()}")
                except ValueError:
                    continue
        
        # Look for any score patterns
        print("\n🔍 Looking for any score patterns...")
        all_elements = driver.find_elements(By.XPATH, "//*[string-length(text()) > 20 and string-length(text()) < 100]")
        
        found_matches = 0
        for elem in all_elements[:50]:  # Check first 50 elements
            try:
                text = elem.text.strip()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                # Look for multi-line pattern: Team1, Team2, Score1, Score2
                if len(lines) >= 4:
                    try:
                        # Check if last two lines are numbers
                        score1 = int(lines[-2])
                        score2 = int(lines[-1])
                        
                        if 0 <= score1 <= 20 and 0 <= score2 <= 20:
                            # Get team names
                            team_lines = []
                            for line in lines[:-2]:
                                if (not line.isdigit() and 
                                    len(line) > 2 and len(line) < 30 and
                                    line not in ['LIVE', 'HT', 'FT']):
                                    team_lines.append(line)
                            
                            if len(team_lines) >= 2:
                                print(f"   🎯 {team_lines[0]} {score1}-{score2} {team_lines[1]}")
                                found_matches += 1
                    
                    except (ValueError, IndexError):
                        continue
            
            except Exception as e:
                continue
        
        if found_matches > 0:
            print(f"✅ Found {found_matches} matches using multi-line detection!")
            return True
        else:
            print("❌ No matches found with multi-line detection")
        
        driver.quit()
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_simple_patterns():
    """Test simple text patterns without Selenium"""
    print("\n📄 Testing simple text patterns...")
    
    import requests
    
    try:
        response = requests.get('https://www.flashscore.com/football/', 
                              headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        
        if response.status_code == 200:
            text = response.text
            print(f"📄 Basic HTML: {len(text)} characters")
            
            # Look for the specific teams we saw
            if "Japan" in text and "Syria" in text:
                print("✅ Found Japan and Syria in basic HTML")
                
                # Look for numbers near these teams
                japan_index = text.find("Japan")
                if japan_index != -1:
                    context = text[japan_index:japan_index+200]
                    numbers = re.findall(r'\d+', context)
                    print(f"Numbers near Japan: {numbers[:10]}")
            
            # Look for any obvious score patterns
            score_matches = re.findall(r'\b\d+\s*[-–]\s*\d+\b', text)
            if score_matches:
                print(f"Score patterns in basic HTML: {score_matches[:10]}")
        
    except Exception as e:
        print(f"❌ Basic request error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Specific Match Detection")
    print("=" * 50)
    
    success = test_flashscore_specific()
    
    if not success:
        test_simple_patterns()
    
    print("\n🚀 Test complete!")