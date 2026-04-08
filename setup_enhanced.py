#!/usr/bin/env python3
"""
Setup Enhanced Scraper
Install dependencies and test the system
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing enhanced scraper requirements...")
    
    try:
        # Install basic requirements
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            'requests', 'beautifulsoup4', 'flask', 'flask-cors', 'lxml'
        ])
        print("✅ Basic requirements installed")
        
        # Try to install Selenium (optional)
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', 
                'selenium', 'webdriver-manager'
            ])
            print("✅ Selenium installed - Enhanced scraping available!")
        except:
            print("⚠️ Selenium installation failed - Basic scraping only")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False

def test_installation():
    """Test if everything is working"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test basic imports
        import requests
        import bs4
        import flask
        print("✅ Basic packages working")
        
        # Test Selenium
        try:
            import selenium
            from webdriver_manager.chrome import ChromeDriverManager
            print("✅ Selenium available - Enhanced scraping ready!")
            selenium_available = True
        except ImportError:
            print("⚠️ Selenium not available - Basic scraping only")
            selenium_available = False
        
        # Test the enhanced scraper
        try:
            from enhanced_scraper import EnhancedScraper
            scraper = EnhancedScraper()
            print("✅ Enhanced scraper loaded successfully")
            
            # Quick test
            print("\n🔍 Quick connectivity test...")
            test_url = 'https://www.livescore.com/en/football/'
            matches = scraper.scrape_basic(test_url)  # Use basic method for quick test
            
            if matches:
                print(f"✅ Found {len(matches)} matches in quick test!")
            else:
                print("⏳ No matches in quick test (normal if no live games)")
            
            return True
            
        except Exception as e:
            print(f"❌ Enhanced scraper test failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Enhanced Scraper Setup")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed - could not install requirements")
        return
    
    # Test installation
    if not test_installation():
        print("❌ Setup failed - installation test failed")
        return
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\n💡 Next steps:")
    print("1. Run: python test_enhanced_scraper.py")
    print("2. Run: python start_realtime.py")
    print("3. Open: http://localhost:3000/live-score-predictor.html")
    print("\n🔧 The enhanced scraper will:")
    print("   - Try Selenium first for JavaScript content")
    print("   - Fall back to basic scraping if needed")
    print("   - Use site-specific CSS selectors")
    print("   - Better pattern matching for scores/teams")

if __name__ == "__main__":
    main()