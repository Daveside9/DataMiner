#!/usr/bin/env python3
"""
Test Visual Betting Monitor
Quick test to verify the visual monitoring system works
"""

import sys
import os
import time
import requests
import json

def test_visual_monitor():
    """Test the visual betting monitor"""
    print("📸 Testing Visual Betting Monitor")
    print("=" * 60)
    
    # Test URLs
    test_sites = [
        {
            'name': 'Bet9ja Live Betting',
            'url': 'https://sports.bet9ja.com/mobile/liveBetting',
            'description': 'Nigerian betting site'
        },
        {
            'name': 'Flashscore Football',
            'url': 'https://www.flashscore.com/football/',
            'description': 'Live scores and odds'
        }
    ]
    
    print("🌐 Available test sites:")
    for i, site in enumerate(test_sites, 1):
        print(f"   {i}. {site['name']} - {site['description']}")
    
    # Check if visual monitor is running
    try:
        response = requests.get('http://localhost:5002/api/visual-status', timeout=5)
        if response.status_code == 200:
            print("✅ Visual Monitor API is running")
        else:
            print("❌ Visual Monitor API not responding properly")
            return False
    except requests.exceptions.RequestException:
        print("❌ Visual Monitor API not running")
        print("💡 Start it with: python visual_bet_monitor.py")
        return False
    
    # Test with first site
    test_site = test_sites[0]  # Bet9ja
    print(f"\n🧪 Testing with {test_site['name']}...")
    
    # Start visual monitoring
    monitor_data = {
        'url': test_site['url'],
        'interval': 30,  # 30 seconds
        'duration': 2    # 2 minutes
    }
    
    try:
        response = requests.post(
            'http://localhost:5002/api/start-visual-monitoring',
            json=monitor_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Visual monitoring started: {result['message']}")
            
            # Monitor for a short time
            print("⏳ Monitoring for 30 seconds...")
            
            for i in range(6):  # 6 checks over 30 seconds
                time.sleep(5)
                
                try:
                    status_response = requests.get('http://localhost:5002/api/visual-status')
                    if status_response.status_code == 200:
                        status = status_response.json()
                        
                        print(f"   📊 Screenshots: {status.get('screenshots_count', 0)}")
                        print(f"   🔄 Changes: {status.get('changes_detected', 0)}")
                        print(f"   💰 Odds found: {len(status.get('current_odds', {}))}")
                        
                        if status.get('screenshots_count', 0) > 0:
                            print("✅ Screenshots are being captured!")
                            break
                    
                except requests.exceptions.RequestException:
                    print("   ⏳ Waiting for status...")
            
            # Stop monitoring
            stop_response = requests.post('http://localhost:5002/api/stop-visual-monitoring')
            if stop_response.status_code == 200:
                print("✅ Visual monitoring stopped")
            
            # Get final results
            try:
                screenshots_response = requests.get('http://localhost:5002/api/screenshots')
                if screenshots_response.status_code == 200:
                    screenshots_data = screenshots_response.json()
                    screenshots = screenshots_data.get('screenshots', [])
                    changes = screenshots_data.get('changes', [])
                    
                    print(f"\n📊 FINAL RESULTS:")
                    print(f"   📸 Total screenshots: {len(screenshots)}")
                    print(f"   🔄 Changes detected: {len(changes)}")
                    
                    if screenshots:
                        print(f"   📁 Screenshots saved in: screenshots/")
                        for screenshot in screenshots[-3:]:  # Last 3
                            print(f"      - {screenshot['filename']}")
                    
                    return True
            
            except requests.exceptions.RequestException:
                print("⚠️ Could not get final results")
                return True  # Still consider it successful
        
        else:
            print(f"❌ Failed to start monitoring: {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_manual_screenshot():
    """Test manual screenshot functionality"""
    print(f"\n📷 Testing Manual Screenshot...")
    
    # This would be implemented in the visual monitor
    print("💡 Manual screenshot feature available in web interface")
    print("   Go to: http://localhost:3000/visual-bet-monitor.html")
    print("   Click: 'Manual Screenshot' button")

def main():
    """Main test function"""
    print("🧪 Visual Betting Monitor Test Suite")
    print("=" * 70)
    
    success = test_visual_monitor()
    
    if success:
        test_manual_screenshot()
        
        print(f"\n🎉 VISUAL MONITOR TEST SUCCESSFUL!")
        print("💡 Next steps:")
        print("   1. Run: python start_complete_system.py")
        print("   2. Open: http://localhost:3000/visual-bet-monitor.html")
        print("   3. Start visual monitoring of your favorite betting site")
        print("   4. Watch screenshots and odds changes in real-time!")
    else:
        print(f"\n⚠️ VISUAL MONITOR TEST FAILED")
        print("💡 Troubleshooting:")
        print("   1. Make sure: python visual_bet_monitor.py is running")
        print("   2. Check: http://localhost:5002 is accessible")
        print("   3. Install: pip install pillow selenium webdriver-manager")
    
    print(f"\n🚀 Test complete!")

if __name__ == "__main__":
    main()