#!/usr/bin/env python3
"""
Simple HTTP server to serve the DataMiner frontend
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080
FRONTEND_DIR = Path(__file__).parent / "frontend"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def end_headers(self):
        # Add CORS headers to allow API calls
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    """Start the frontend server"""
    print("🌐 DataMiner Frontend Server")
    print("=" * 40)
    
    # Check if frontend directory exists
    if not FRONTEND_DIR.exists():
        print(f"❌ Frontend directory not found: {FRONTEND_DIR}")
        return
    
    # Check if index.html exists
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        print(f"❌ index.html not found: {index_file}")
        return
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"🚀 Server starting on port {PORT}")
            print(f"📁 Serving files from: {FRONTEND_DIR}")
            print(f"🌐 Frontend URL: http://localhost:{PORT}")
            print(f"🔧 API URL: http://localhost:5000/api")
            print("\n📋 Instructions:")
            print("1. Make sure the DataMiner API is running (python backend/app.py)")
            print("2. Open your browser to http://localhost:8080")
            print("3. Try scraping some websites!")
            print("\nPress Ctrl+C to stop the server")
            print("=" * 40)
            
            # Try to open browser automatically
            try:
                webbrowser.open(f"http://localhost:{PORT}")
                print("🌐 Browser opened automatically")
            except:
                print("⚠️ Could not open browser automatically")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except OSError as e:
        if e.errno == 10048:  # Port already in use
            print(f"❌ Port {PORT} is already in use. Try a different port or stop the existing server.")
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()