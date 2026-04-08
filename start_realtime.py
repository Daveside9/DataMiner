#!/usr/bin/env python3
"""
Start Real-Time Sports Monitoring System
One command to start everything
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
import http.server
import socketserver

def start_backend():
    """Start the real-time backend"""
    print("🔧 Starting Real-Time Backend...")
    try:
        subprocess.Popen([sys.executable, 'real_time_system.py'])
        time.sleep(3)  # Wait for backend to start
        print("✅ Backend started on http://localhost:5001")
        return True
    except Exception as e:
        print(f"❌ Backend failed: {e}")
        return False

def start_frontend():
    """Start the frontend server"""
    print("🌐 Starting Frontend Server...")
    
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory='frontend', **kwargs)
        
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            super().end_headers()
    
    try:
        httpd = socketserver.TCPServer(("", 3000), CustomHandler)
        print("✅ Frontend started on http://localhost:3000")
        
        # Open browser
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:3000/live-score-predictor.html')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        return httpd
    except Exception as e:
        print(f"❌ Frontend failed: {e}")
        return None

def main():
    """Main startup function"""
    print("🎯 Real-Time Sports Monitoring System")
    print("=" * 60)
    print("🚀 Starting complete system...")
    print("📡 Backend: Live score scraping & AI prediction")
    print("🌐 Frontend: Visual monitoring interface")
    print("🤖 Features: Real-time data + Score prediction")
    print("=" * 60)
    
    # Start backend
    if not start_backend():
        print("❌ Failed to start backend")
        return
    
    # Start frontend
    frontend_server = start_frontend()
    if not frontend_server:
        print("❌ Failed to start frontend")
        return
    
    print("\n" + "=" * 60)
    print("🎉 SYSTEM READY!")
    print("📊 Live Score Predictor: http://localhost:3000/live-score-predictor.html")
    print("🔧 Backend API: http://localhost:5001")
    print("\n💡 How to use:")
    print("1. Browser opens automatically to the Live Score Predictor")
    print("2. Click 'Start Live Monitoring' to begin")
    print("3. Watch real-time scores and AI predictions")
    print("4. System monitors betting sites for live data")
    print("\n🛑 Press Ctrl+C to stop both servers")
    print("=" * 60)
    
    try:
        frontend_server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")
        print("✅ All servers shut down")

if __name__ == "__main__":
    main()