#!/usr/bin/env python3
"""
DataMiner Complete Startup Script
Starts both backend and frontend servers
"""

import os
import sys
import subprocess
import threading
import time
import requests
import webbrowser

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS', 
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'selenium': 'selenium',
        'webdriver_manager': 'webdriver-manager'
    }
    
    missing_packages = []
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name}")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n💡 Install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def start_backend():
    """Start the backend server in a separate process"""
    print("\n🔧 Starting Backend Server...")
    
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found")
        return None
    
    try:
        # Start backend process
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if backend is running
        for attempt in range(10):
            try:
                response = requests.get('http://localhost:5000/api/health', timeout=2)
                if response.status_code == 200:
                    print("✅ Backend server started successfully!")
                    print("📍 Backend API: http://localhost:5000")
                    return process
            except:
                time.sleep(1)
        
        print("❌ Backend failed to start properly")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the frontend server"""
    print("\n🌐 Starting Frontend Server...")
    
    import http.server
    import socketserver
    
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), 'frontend'), **kwargs)
        
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
    
    PORT = 3000
    
    try:
        httpd = socketserver.TCPServer(("", PORT), CustomHandler)
        print("✅ Frontend server started successfully!")
        print(f"📍 Frontend: http://localhost:{PORT}")
        
        # Open browser
        def open_browser():
            time.sleep(1)
            webbrowser.open(f'http://localhost:{PORT}/historical-pattern-scraper.html')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        return httpd
        
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def main():
    """Main startup function"""
    print("🚀 DataMiner Complete Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend")
        return
    
    # Start frontend
    frontend_server = start_frontend()
    if not frontend_server:
        print("❌ Failed to start frontend")
        backend_process.terminate()
        return
    
    print("\n" + "=" * 50)
    print("🎉 DataMiner is now running!")
    print("📊 Historical Pattern Scraper: http://localhost:3000/historical-pattern-scraper.html")
    print("🔧 Backend API: http://localhost:5000")
    print("\n💡 Usage Instructions:")
    print("1. The browser should open automatically")
    print("2. Enter a sports website URL (e.g., BBC Sport, Livescore)")
    print("3. Enter team name (e.g., 'Real Madrid')")
    print("4. Click '🧪 Test Selectors' first to verify they work")
    print("5. Click '🚀 Start Historical Scraping' to analyze patterns")
    print("\n🛑 Press Ctrl+C to stop both servers")
    print("=" * 50)
    
    try:
        # Keep both servers running
        frontend_server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down DataMiner...")
        frontend_server.shutdown()
        backend_process.terminate()
        print("✅ DataMiner stopped successfully")

if __name__ == "__main__":
    main()