#!/usr/bin/env python3
"""
Start DataMiner Backend Server
"""

import os
import sys
import subprocess
import time
import requests

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'flask-cors', 'requests', 'beautifulsoup4', 
        'selenium', 'webdriver-manager'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def start_backend():
    """Start the Flask backend server"""
    print("🚀 Starting DataMiner Backend Server...")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        return False
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found")
        return False
    
    # Start the Flask app
    try:
        print("🔧 Starting Flask server...")
        print("📍 Backend will run on: http://localhost:5000")
        print("🌐 Frontend available at: http://localhost:3000")
        print("📊 Historical scraper: http://localhost:3000/historical-pattern-scraper.html")
        print("\n⏳ Starting server (this may take a moment)...")
        
        # Run the Flask app
        os.chdir(backend_dir)
        subprocess.run([sys.executable, 'app.py'], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_backend():
    """Test if backend is running"""
    print("🔍 Testing backend connection...")
    
    for attempt in range(5):
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=2)
            if response.status_code == 200:
                print("✅ Backend is running successfully!")
                return True
        except:
            time.sleep(1)
    
    print("❌ Backend is not responding")
    return False

def main():
    """Main function"""
    print("🎯 DataMiner Backend Starter")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Just test the backend
        test_backend()
    else:
        # Start the backend
        start_backend()

if __name__ == "__main__":
    main()