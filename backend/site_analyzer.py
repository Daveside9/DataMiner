#!/usr/bin/env python3
"""
Site Structure Analyzer - Analyze website structure and suggest CSS selectors
"""

from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json
from collections import Counter
import re

def analyze_site_structure(url):
    """Analyze a website's structure and suggest CSS selectors"""
    try:
        # Fetch the website
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        analysis = {
            "url": url,
            "title": soup.find('title').get_text(strip=True) if soup.find('title') else "No title",
            "structure": analyze_html_structure(soup),
            "suggested_selectors": suggest_sports_selectors(soup),
            "common_patterns": find_common_patterns(soup),
            "data_elements": find_data_elements(soup)
        }
        
        return analysis
        
    except Exception as e:
        return {"error": str(e)}

def analyze_html_structure(soup):
    """Analyze the HTML structure"""
    structure = {
        "total_elements": len(soup.find_all()),
        "headings": {},
        "lists": 0,
        "tables": 0,
        "forms": 0,
        "links": 0,
        "images": 0,
        "common_classes": [],
        "common_ids": []
    }
    
    # Count headings
    for i in range(1, 7):
        headings = soup.find_all(f'h{i}')
        if headings:
            structure["headings"][f'h{i}'] = len(headings)
    
    # Count other elements
    structure["lists"] = len(soup.find_all(['ul', 'ol']))
    structure["tables"] = len(soup.find_all('table'))
    structure["forms"] = len(soup.find_all('form'))
    structure["links"] = len(soup.find_all('a'))
    structure["images"] = len(soup.find_all('img'))
    
    # Find common classes and IDs
    all_classes = []
    all_ids = []
    
    for element in soup.find_all():
        if element.get('class'):
            all_classes.extend(element.get('class'))
        if element.get('id'):
            all_ids.append(element.get('id'))
    
    # Get most common classes and IDs
    class_counter = Counter(all_classes)
    id_counter = Counter(all_ids)
    
    structure["common_classes"] = [{"class": cls, "count": count} for cls, count in class_counter.most_common(10)]
    structure["common_ids"] = [{"id": id_name, "count": count} for id_name, count in id_counter.most_common(10)]
    
    return structure

def suggest_sports_selectors(soup):
    """Suggest CSS selectors for sports data"""
    suggestions = {
        "teams": [],
        "scores": [],
        "times": [],
        "matches": [],
        "leagues": []
    }
    
    # Look for team-related elements
    team_keywords = ['team', 'club', 'home', 'away', 'opponent']
    for keyword in team_keywords:
        # Class-based selectors
        elements = soup.find_all(class_=re.compile(keyword, re.I))
        if elements:
            for elem in elements[:3]:  # Limit to first 3
                classes = ' '.join(elem.get('class', []))
                suggestions["teams"].append({
                    "selector": f".{classes.replace(' ', '.')}",
                    "sample_text": elem.get_text(strip=True)[:50],
                    "count": len(soup.find_all(class_=elem.get('class')))
                })
    
    # Look for score-related elements
    score_keywords = ['score', 'result', 'goal', 'point']
    for keyword in score_keywords:
        elements = soup.find_all(class_=re.compile(keyword, re.I))
        if elements:
            for elem in elements[:3]:
                classes = ' '.join(elem.get('class', []))
                suggestions["scores"].append({
                    "selector": f".{classes.replace(' ', '.')}",
                    "sample_text": elem.get_text(strip=True)[:50],
                    "count": len(soup.find_all(class_=elem.get('class')))
                })
    
    # Look for time/date elements
    time_keywords = ['time', 'date', 'kick', 'start', 'match']
    for keyword in time_keywords:
        elements = soup.find_all(class_=re.compile(keyword, re.I))
        if elements:
            for elem in elements[:3]:
                classes = ' '.join(elem.get('class', []))
                suggestions["times"].append({
                    "selector": f".{classes.replace(' ', '.')}",
                    "sample_text": elem.get_text(strip=True)[:50],
                    "count": len(soup.find_all(class_=elem.get('class')))
                })
    
    # Look for match containers
    match_keywords = ['match', 'fixture', 'game', 'event']
    for keyword in match_keywords:
        elements = soup.find_all(class_=re.compile(keyword, re.I))
        if elements:
            for elem in elements[:3]:
                classes = ' '.join(elem.get('class', []))
                suggestions["matches"].append({
                    "selector": f".{classes.replace(' ', '.')}",
                    "sample_text": elem.get_text(strip=True)[:100],
                    "count": len(soup.find_all(class_=elem.get('class')))
                })
    
    # Look for league/competition elements
    league_keywords = ['league', 'competition', 'tournament', 'cup']
    for keyword in league_keywords:
        elements = soup.find_all(class_=re.compile(keyword, re.I))
        if elements:
            for elem in elements[:3]:
                classes = ' '.join(elem.get('class', []))
                suggestions["leagues"].append({
                    "selector": f".{classes.replace(' ', '.')}",
                    "sample_text": elem.get_text(strip=True)[:50],
                    "count": len(soup.find_all(class_=elem.get('class')))
                })
    
    return suggestions

def find_common_patterns(soup):
    """Find common HTML patterns that might contain data"""
    patterns = {
        "repeated_structures": [],
        "data_tables": [],
        "list_items": [],
        "card_layouts": []
    }
    
    # Find repeated class patterns
    class_counts = Counter()
    for element in soup.find_all():
        if element.get('class'):
            class_name = ' '.join(element.get('class'))
            class_counts[class_name] += 1
    
    # Get classes that appear multiple times (likely repeated structures)
    for class_name, count in class_counts.most_common(10):
        if count > 2:  # Only classes that appear more than twice
            sample_element = soup.find(class_=class_name.split())
            patterns["repeated_structures"].append({
                "class": class_name,
                "count": count,
                "selector": f".{class_name.replace(' ', '.')}",
                "sample_text": sample_element.get_text(strip=True)[:100] if sample_element else ""
            })
    
    # Find tables
    tables = soup.find_all('table')
    for i, table in enumerate(tables[:5]):  # Limit to first 5 tables
        rows = table.find_all('tr')
        patterns["data_tables"].append({
            "selector": f"table:nth-of-type({i+1})",
            "rows": len(rows),
            "columns": len(rows[0].find_all(['td', 'th'])) if rows else 0,
            "sample_headers": [th.get_text(strip=True) for th in rows[0].find_all('th')][:5] if rows else []
        })
    
    # Find list patterns
    lists = soup.find_all(['ul', 'ol'])
    for i, list_elem in enumerate(lists[:5]):
        items = list_elem.find_all('li')
        patterns["list_items"].append({
            "selector": f"{'ul' if list_elem.name == 'ul' else 'ol'}:nth-of-type({i+1}) li",
            "count": len(items),
            "sample_items": [li.get_text(strip=True)[:50] for li in items[:3]]
        })
    
    return patterns

def find_data_elements(soup):
    """Find elements that likely contain data"""
    data_elements = []
    
    # Look for elements with numbers (likely scores, dates, etc.)
    number_pattern = re.compile(r'\d+')
    
    for element in soup.find_all():
        text = element.get_text(strip=True)
        if text and number_pattern.search(text) and len(text) < 100:
            # Skip if it's just a number
            if not text.isdigit():
                classes = ' '.join(element.get('class', []))
                data_elements.append({
                    "tag": element.name,
                    "class": classes,
                    "selector": f"{element.name}.{classes.replace(' ', '.')}" if classes else element.name,
                    "text": text[:50],
                    "likely_data_type": guess_data_type(text)
                })
    
    # Remove duplicates and limit results
    seen = set()
    unique_elements = []
    for elem in data_elements:
        key = (elem["selector"], elem["text"])
        if key not in seen:
            seen.add(key)
            unique_elements.append(elem)
    
    return unique_elements[:20]  # Limit to 20 elements

def guess_data_type(text):
    """Guess what type of data this might be"""
    text = text.lower().strip()
    
    # Time patterns
    if re.search(r'\d{1,2}:\d{2}', text):
        return "time"
    
    # Date patterns
    if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text):
        return "date"
    
    # Score patterns
    if re.search(r'\d+\s*[-:]\s*\d+', text):
        return "score"
    
    # Team name patterns (contains letters and might have numbers)
    if re.search(r'[a-z]', text) and len(text) > 3:
        return "team_name"
    
    # Pure numbers
    if text.isdigit():
        return "number"
    
    return "text"

def main():
    """Test the site analyzer"""
    test_urls = [
        "https://www.bbc.com/sport/football/scores-fixtures",
        "https://quotes.toscrape.com/",
        "https://news.ycombinator.com/"
    ]
    
    for url in test_urls:
        print(f"\n🔍 Analyzing: {url}")
        print("=" * 60)
        
        analysis = analyze_site_structure(url)
        
        if "error" in analysis:
            print(f"❌ Error: {analysis['error']}")
            continue
        
        print(f"📄 Title: {analysis['title']}")
        print(f"📊 Total elements: {analysis['structure']['total_elements']}")
        
        # Show suggested selectors
        print(f"\n🎯 Suggested Sports Selectors:")
        for category, suggestions in analysis['suggested_selectors'].items():
            if suggestions:
                print(f"  {category.upper()}:")
                for suggestion in suggestions[:2]:  # Show top 2
                    print(f"    • {suggestion['selector']} ({suggestion['count']} elements)")
                    print(f"      Sample: {suggestion['sample_text']}")
        
        # Show common patterns
        print(f"\n🔄 Repeated Structures:")
        for pattern in analysis['common_patterns']['repeated_structures'][:3]:
            print(f"  • {pattern['selector']} ({pattern['count']} times)")
            print(f"    Sample: {pattern['sample_text'][:50]}...")

if __name__ == "__main__":
    main()