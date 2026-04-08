#!/usr/bin/env python3
"""
Test script for DataMiner web scraper
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from scraper.web_scraper import WebScraper
from database.db_manager import DatabaseManager
from analyzer.pattern_analyzer import PatternAnalyzer

def test_basic_scraping():
    """Test basic web scraping functionality"""
    print("🧪 Testing DataMiner Web Scraper...")
    
    scraper = WebScraper()
    
    # Test with a simple website
    test_url = "https://httpbin.org/json"
    print(f"📡 Testing scraping: {test_url}")
    
    result = scraper.scrape_url(test_url)
    
    if "error" in result:
        print(f"❌ Scraping failed: {result['error']}")
        return False
    else:
        print("✅ Scraping successful!")
        print(f"📊 Data collected: {len(str(result))} characters")
        return True

def test_database():
    """Test database functionality"""
    print("\n🗄️ Testing Database Manager...")
    
    db_manager = DatabaseManager("data/test.db")
    db_manager.init_database()
    
    # Test adding a data source
    success = db_manager.add_data_source(
        name="test_source",
        url="https://example.com",
        description="Test data source"
    )
    
    if success:
        print("✅ Database operations successful!")
        return True
    else:
        print("❌ Database operations failed!")
        return False

def test_analysis():
    """Test pattern analysis"""
    print("\n📈 Testing Pattern Analyzer...")
    
    analyzer = PatternAnalyzer()
    
    # Create sample data
    sample_data = [
        {
            'timestamp': '2024-01-01T10:00:00',
            'success': True,
            'method': 'requests',
            'data': {'value': 100, 'text': 'sample text'}
        },
        {
            'timestamp': '2024-01-01T11:00:00',
            'success': True,
            'method': 'requests',
            'data': {'value': 105, 'text': 'another sample'}
        }
    ]
    
    analysis = analyzer.analyze_trends(sample_data)
    
    if "error" in analysis:
        print(f"❌ Analysis failed: {analysis['error']}")
        return False
    else:
        print("✅ Analysis successful!")
        print(f"📊 Generated {len(analysis.get('insights', []))} insights")
        return True

def main():
    """Run all tests"""
    print("🚀 DataMiner Test Suite")
    print("=" * 50)
    
    tests = [
        ("Web Scraper", test_basic_scraping),
        ("Database Manager", test_database),
        ("Pattern Analyzer", test_analysis)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! DataMiner is ready to use.")
        print("\n🚀 Next steps:")
        print("  1. Run: python backend/app.py")
        print("  2. Visit: http://localhost:5000/api/health")
        print("  3. Start building the frontend dashboard!")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()