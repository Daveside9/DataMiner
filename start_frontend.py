#!/usr/bin/env python3
"""
Start DataMiner Frontend Server
"""

import os
import http.server
import socketserver
import webbrowser
import threading
import time

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), 'frontend'), **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_frontend_server():
    """Start the frontend server"""
    PORT = 3000
    
    print("🌐 Starting DataMiner Frontend Server...")
    print("=" * 50)
    print(f"📍 Server running on: http://localhost:{PORT}")
    print("📊 Available interfaces:")
    print(f"   • Main Dashboard: http://localhost:{PORT}/index.html")
    print(f"   • Historical Scraper: http://localhost:{PORT}/historical-pattern-scraper.html")
    print(f"   • Visual Inspector: http://localhost:{PORT}/visual-inspector.html")
    print(f"   • Pattern Analyzer: http://localhost:{PORT}/pattern-analyzer.html")
    print(f"   • Screen Monitor: http://localhost:{PORT}/screen-monitor.html")
    print("\n⚠️  Make sure backend is running: python start_backend.py")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            # Open browser after a short delay
            def open_browser():
                time.sleep(1)
                webbrowser.open(f'http://localhost:{PORT}/historical-pattern-scraper.html')
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            print(f"✅ Frontend server started successfully!")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use")
            print("💡 Try a different port or stop the existing server")
        else:
            print(f"❌ Error starting server: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    start_frontend_server()