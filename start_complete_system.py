#!/usr/bin/env python3
"""
Complete Sports & Betting Monitor System Launcher
Starts both the real-time scraper and visual monitor together
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
import http.server
import socketserver
from pathlib import Path

class CompleteBettingSystem:
    def __init__(self):
        self.processes = []
        self.servers = []
    
    def start_realtime_backend(self):
        """Start the real-time sports monitoring backend"""
        print("🚀 Starting Real-Time Sports Backend (Port 5001)...")
        try:
            process = subprocess.Popen([sys.executable, 'real_time_system.py'])
            self.processes.append(('Real-Time Backend', process))
            time.sleep(3)
            print("✅ Real-Time Backend started")
            return True
        except Exception as e:
            print(f"❌ Real-Time Backend failed: {e}")
            return False
    
    def start_visual_monitor_backend(self):
        """Start the visual betting monitor backend"""
        print("📸 Starting Visual Monitor Backend (Port 5002)...")
        try:
            process = subprocess.Popen([sys.executable, 'visual_bet_monitor.py'])
            self.processes.append(('Visual Monitor Backend', process))
            time.sleep(3)
            print("✅ Visual Monitor Backend started")
            return True
        except Exception as e:
            print(f"❌ Visual Monitor Backend failed: {e}")
            return False
    
    def start_frontend_server(self):
        """Start the frontend server for all interfaces"""
        print("🌐 Starting Frontend Server (Port 3000)...")
        
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory='frontend', **kwargs)
            
            def end_headers(self):
                self.send_header('Access-Control-Allow-Origin', '*')
                super().end_headers()
        
        try:
            httpd = socketserver.TCPServer(("", 3000), CustomHandler)
            self.servers.append(('Frontend Server', httpd))
            print("✅ Frontend Server started")
            return httpd
        except Exception as e:
            print(f"❌ Frontend Server failed: {e}")
            return None
    
    def open_browser_interfaces(self):
        """Open browser tabs for all interfaces"""
        print("🌐 Opening browser interfaces...")
        
        def open_tabs():
            time.sleep(5)  # Wait for servers to be ready
            
            # Main dashboard
            webbrowser.open('http://localhost:3000/live-score-predictor.html')
            time.sleep(2)
            
            # Visual monitor
            webbrowser.open('http://localhost:3000/visual-bet-monitor.html')
            time.sleep(2)
            
            # Optional: Open other tools
            # webbrowser.open('http://localhost:3000/visual-inspector.html')
        
        threading.Thread(target=open_tabs, daemon=True).start()
    
    def display_system_info(self):
        """Display system information and URLs"""
        print("\n" + "=" * 80)
        print("🎉 COMPLETE BETTING MONITORING SYSTEM READY!")
        print("=" * 80)
        
        print("\n📡 BACKEND SERVICES:")
        print("   🎯 Real-Time Sports API:    http://localhost:5001")
        print("   📸 Visual Monitor API:      http://localhost:5002")
        
        print("\n🌐 WEB INTERFACES:")
        print("   ⚽ Live Score Predictor:    http://localhost:3000/live-score-predictor.html")
        print("   📸 Visual Bet Monitor:      http://localhost:3000/visual-bet-monitor.html")
        print("   🔍 Visual Inspector:        http://localhost:3000/visual-inspector.html")
        print("   📊 Pattern Analyzer:        http://localhost:3000/pattern-analyzer.html")
        
        print("\n🎯 SYSTEM CAPABILITIES:")
        print("   ✅ Real-time live score scraping (Flashscore, Bet9ja)")
        print("   ✅ AI-powered score predictions")
        print("   ✅ Team-specific monitoring")
        print("   ✅ Visual screenshot monitoring")
        print("   ✅ Betting odds change detection")
        print("   ✅ Pattern analysis and trends")
        
        print("\n💡 QUICK START GUIDE:")
        print("   1. Browser tabs opened automatically")
        print("   2. Use 'Live Score Predictor' for data scraping + AI predictions")
        print("   3. Use 'Visual Bet Monitor' for screenshot monitoring")
        print("   4. Select Flashscore.com for best live match results")
        print("   5. Select Bet9ja for Nigerian betting site monitoring")
        
        print("\n🛑 TO STOP: Press Ctrl+C")
        print("=" * 80)
    
    def cleanup(self):
        """Clean up all processes and servers"""
        print("\n🛑 Shutting down system...")
        
        # Stop all processes
        for name, process in self.processes:
            try:
                process.terminate()
                print(f"✅ Stopped {name}")
            except:
                pass
        
        # Stop all servers
        for name, server in self.servers:
            try:
                server.shutdown()
                print(f"✅ Stopped {name}")
            except:
                pass
        
        print("✅ All services stopped")
    
    def run(self):
        """Run the complete system"""
        print("🎯 Complete Sports & Betting Monitor System")
        print("=" * 60)
        print("🚀 Starting all services...")
        
        try:
            # Start backend services
            realtime_ok = self.start_realtime_backend()
            visual_ok = self.start_visual_monitor_backend()
            
            if not any([realtime_ok, visual_ok]):
                print("❌ Failed to start any backend services")
                return
            
            # Start frontend server
            frontend_server = self.start_frontend_server()
            if not frontend_server:
                print("❌ Failed to start frontend server")
                return
            
            # Open browser interfaces
            self.open_browser_interfaces()
            
            # Display system info
            self.display_system_info()
            
            # Keep the system running
            try:
                frontend_server.serve_forever()
            except KeyboardInterrupt:
                pass
        
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

def main():
    """Main function"""
    system = CompleteBettingSystem()
    system.run()

if __name__ == "__main__":
    main()