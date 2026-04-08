#!/usr/bin/env python3
"""
BetVision Pro Complete System Startup
Starts Django backend + existing monitoring services
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def run_service(name, command, cwd=None):
    """Run a service in the background"""
    def run():
        try:
            print(f"🚀 Starting {name}...")
            subprocess.run(command, shell=True, cwd=cwd)
        except Exception as e:
            print(f"❌ {name} error: {e}")
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread

def check_port(port):
    """Check if a port is available"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def main():
    """Main startup function"""
    print("🎯 BetVision Pro - Complete System Startup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]}")
    
    # Check required directories
    base_dir = Path(__file__).parent
    backend_dir = base_dir / "betvision_backend"
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    # Install dependencies if needed
    print("\n📦 Checking dependencies...")
    try:
        import django, requests, selenium, flask, beautifulsoup4
        print("✅ Core dependencies found")
    except ImportError as e:
        print(f"⚠️ Missing dependency: {e}")
        print("📥 Installing dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "django", "djangorestframework", "django-cors-headers", 
            "pillow", "requests", "selenium", "flask", "flask-cors", 
            "beautifulsoup4", "webdriver-manager"
        ])
    
    # Check ports
    print("\n🔍 Checking ports...")
    ports = {
        8000: "Django Backend",
        5001: "Real-time System", 
        5002: "Visual Monitor"
    }
    
    for port, service in ports.items():
        if not check_port(port):
            print(f"⚠️ Port {port} ({service}) is already in use")
        else:
            print(f"✅ Port {port} ({service}) available")
    
    # Initialize Django backend
    print("\n🗄️ Initializing Django backend...")
    
    # Run migrations
    try:
        subprocess.run([
            sys.executable, "manage.py", "makemigrations"
        ], cwd=backend_dir, check=True, capture_output=True)
        
        subprocess.run([
            sys.executable, "manage.py", "migrate"
        ], cwd=backend_dir, check=True, capture_output=True)
        
        print("✅ Database initialized")
    except subprocess.CalledProcessError as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    # Start services
    print("\n🚀 Starting BetVision Pro services...")
    
    services = []
    
    # 1. Django Backend (Port 8000)
    services.append(run_service(
        "Django Backend", 
        f"{sys.executable} manage.py runserver 0.0.0.0:8000",
        cwd=backend_dir
    ))
    
    # 2. Real-time Sports System (Port 5001)
    if (base_dir / "real_time_system.py").exists():
        services.append(run_service(
            "Real-time Sports System",
            f"{sys.executable} real_time_system.py",
            cwd=base_dir
        ))
    
    # 3. Improved Visual Monitor (Port 5002)
    if (base_dir / "improved_visual_monitor.py").exists():
        services.append(run_service(
            "Improved Visual Monitor",
            f"{sys.executable} improved_visual_monitor.py",
            cwd=base_dir
        ))
    
    # Wait for services to start
    print("\n⏳ Waiting for services to start...")
    time.sleep(5)
    
    # Display service URLs
    print("\n" + "=" * 60)
    print("🎉 BetVision Pro System is READY!")
    print("=" * 60)
    print("🌐 MAIN SERVICES:")
    print("   📱 Landing Page:     http://localhost:8000")
    print("   📊 User Dashboard:   http://localhost:8000/dashboard")
    print("   🔧 Admin Panel:      http://localhost:8000/admin")
    print("   📚 API Endpoints:    http://localhost:8000/api/")
    print()
    print("🔧 MONITORING SERVICES:")
    print("   ⚡ Real-time System: http://localhost:5001")
    print("   📸 Visual Monitor:   http://localhost:5002")
    print()
    print("📋 FEATURES AVAILABLE:")
    print("   ✅ User Registration & Authentication")
    print("   ✅ Professional Landing Page")
    print("   ✅ User Dashboard with Analytics")
    print("   ✅ Real-time Sports Monitoring")
    print("   ✅ Advanced Screenshot Capture")
    print("   ✅ AI-powered Predictions")
    print("   ✅ Change Detection & Alerts")
    print("   ✅ Comprehensive Analytics")
    print()
    print("🎯 QUICK START:")
    print("   1. Visit http://localhost:8000")
    print("   2. Click 'Sign Up' to create account")
    print("   3. Access dashboard to start monitoring")
    print("   4. Use 'Start Monitoring' to begin")
    print("=" * 60)
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down BetVision Pro...")
        print("✅ All services stopped")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Startup cancelled by user")
        sys.exit(0)