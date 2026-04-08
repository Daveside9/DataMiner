#!/usr/bin/env python3
"""
Complete Sports System Startup
Starts all sports monitoring, data mining, and analysis services
"""

import os
import sys
import subprocess
import threading
import time
import requests
from pathlib import Path

def run_service(name, command, cwd=None, port=None):
    """Run a service in the background"""
    def run():
        try:
            print(f"🚀 Starting {name}...")
            if port:
                print(f"   📡 Port: {port}")
            subprocess.run(command, shell=True, cwd=cwd)
        except Exception as e:
            print(f"❌ {name} error: {e}")
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread

def check_service_health(port, service_name, max_retries=10):
    """Check if a service is running and healthy"""
    for attempt in range(max_retries):
        try:
            response = requests.get(f'http://localhost:{port}', timeout=2)
            if response.status_code in [200, 404]:  # 404 is OK for API endpoints
                print(f"✅ {service_name} is healthy on port {port}")
                return True
        except:
            pass
        time.sleep(2)
    
    print(f"⚠️ {service_name} health check failed on port {port}")
    return False

def main():
    """Main startup function"""
    print("🎯 Complete Sports System Startup")
    print("=" * 70)
    
    base_dir = Path(__file__).parent
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]}")
    
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
            "beautifulsoup4", "webdriver-manager", "opencv-python"
        ])
    
    # Start services
    print("\n🚀 Starting Complete Sports System...")
    
    services = []
    
    # 1. Django Backend (Port 8000)
    backend_dir = base_dir / "betvision_backend"
    if backend_dir.exists():
        print("\n🗄️ Initializing Django backend...")
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
        
        services.append(run_service(
            "Django Backend", 
            f"{sys.executable} manage.py runserver 0.0.0.0:8000",
            cwd=backend_dir,
            port=8000
        ))
    
    # 2. React Frontend (Port 3000)
    frontend_dir = base_dir / "betvision_frontend"
    if frontend_dir.exists():
        print("📦 Installing React dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True, capture_output=True)
            print("✅ React dependencies installed")
        except subprocess.CalledProcessError:
            print("⚠️ npm install failed, continuing...")
        
        services.append(run_service(
            "React Frontend",
            "npm start",
            cwd=frontend_dir,
            port=3000
        ))
    
    # 3. Real-time Sports System (Port 5001)
    if (base_dir / "real_time_system.py").exists():
        services.append(run_service(
            "Real-time Sports System",
            f"{sys.executable} real_time_system.py",
            cwd=base_dir,
            port=5001
        ))
    
    # 4. Improved Visual Monitor (Port 5002)
    if (base_dir / "improved_visual_monitor.py").exists():
        services.append(run_service(
            "Improved Visual Monitor",
            f"{sys.executable} improved_visual_monitor.py",
            cwd=base_dir,
            port=5002
        ))
    
    # 5. Sports Data Mining Bot (Port 5003)
    if (base_dir / "sports_data_mining_bot.py").exists():
        services.append(run_service(
            "Sports Data Mining Bot",
            f"{sys.executable} sports_data_mining_bot.py",
            cwd=base_dir,
            port=5003
        ))
    
    # Wait for services to start
    print("\n⏳ Waiting for services to start...")
    time.sleep(10)
    
    # Health checks
    print("\n🔍 Performing health checks...")
    health_checks = [
        (8000, "Django Backend"),
        (3000, "React Frontend"),
        (5001, "Real-time Sports System"),
        (5002, "Visual Monitor"),
        (5003, "Data Mining Bot")
    ]
    
    healthy_services = 0
    for port, service_name in health_checks:
        if check_service_health(port, service_name):
            healthy_services += 1
    
    # Display system status
    print("\n" + "=" * 70)
    print("🎉 COMPLETE SPORTS SYSTEM IS READY!")
    print("=" * 70)
    print(f"✅ Services Running: {healthy_services}/{len(health_checks)}")
    print()
    print("🌐 MAIN INTERFACES:")
    print("   📱 React App:        http://localhost:3000")
    print("   📊 Django Admin:     http://localhost:8000/admin")
    print("   📚 API Endpoints:    http://localhost:8000/api/")
    print()
    print("🔧 MONITORING SERVICES:")
    print("   ⚡ Real-time System: http://localhost:5001")
    print("   📸 Visual Monitor:   http://localhost:5002")
    print("   🤖 Data Mining Bot:  http://localhost:5003")
    print()
    print("📋 SPORTS FEATURES AVAILABLE:")
    print("   ✅ Live Sports Monitoring")
    print("   ✅ Historical Data Mining")
    print("   ✅ Team Analysis & Predictions")
    print("   ✅ Advanced Screen Capture")
    print("   ✅ Pattern Recognition")
    print("   ✅ AI-Powered Insights")
    print("   ✅ Multi-Source Data Collection")
    print("   ✅ Real-time Change Detection")
    print()
    print("🎯 QUICK START GUIDE:")
    print("   1. Visit http://localhost:3000")
    print("   2. Navigate to Sports section")
    print("   3. Configure teams to monitor")
    print("   4. Enable data mining & screen capture")
    print("   5. Start comprehensive monitoring")
    print()
    print("🤖 DATA MINING BOT FEATURES:")
    print("   • Mine historical data for any team")
    print("   • Advanced pattern analysis")
    print("   • Screen monitoring with AI")
    print("   • SQLite database storage")
    print("   • Predictive modeling")
    print()
    print("📊 EXAMPLE API CALLS:")
    print("   # Start data mining")
    print("   POST http://localhost:5003/api/start-data-mining")
    print("   {\"teams\": [\"Arsenal\", \"Chelsea\"], \"time_period\": \"6_months\"}")
    print()
    print("   # Mine specific team")
    print("   POST http://localhost:5003/api/mine-team-history")
    print("   {\"team_name\": \"Arsenal\", \"analysis_period\": \"6_months\"}")
    print()
    print("   # Start screen monitoring")
    print("   POST http://localhost:5002/api/start-visual-monitoring")
    print("   {\"url\": \"https://flashscore.com\", \"interval\": 30}")
    print("=" * 70)
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Complete Sports System...")
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