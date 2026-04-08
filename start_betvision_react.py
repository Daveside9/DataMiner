#!/usr/bin/env python3
"""
BetVision Pro - React + Django Startup Script
Starts React frontend (port 3000) + Django backend (port 8000) + monitoring services
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path
import json

def run_service(name, command, cwd=None, shell=True):
    """Run a service in the background"""
    def run():
        try:
            print(f"🚀 Starting {name}...")
            if shell:
                subprocess.run(command, shell=True, cwd=cwd)
            else:
                subprocess.run(command, cwd=cwd)
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

def check_node_npm():
    """Check if Node.js and npm are installed"""
    try:
        node_result = subprocess.run(['node', '--version'], capture_output=True, text=True, shell=True)
        npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True, shell=True)
        
        if node_result.returncode == 0 and npm_result.returncode == 0:
            print(f"✅ Node.js {node_result.stdout.strip()}")
            print(f"✅ npm {npm_result.stdout.strip()}")
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking Node.js: {e}")
        return False

def install_react_dependencies(frontend_dir):
    """Install React dependencies"""
    print("📦 Installing React dependencies...")
    try:
        subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True, shell=True)
        print("✅ React dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install React dependencies: {e}")
        return False

def main():
    """Main startup function"""
    print("🎯 BetVision Pro - React + Django System Startup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]}")
    
    # Check Node.js and npm
    if not check_node_npm():
        print("❌ Node.js and npm are required for React frontend")
        print("📥 Please install Node.js from https://nodejs.org/")
        return False
    
    # Check required directories
    base_dir = Path(__file__).parent
    backend_dir = base_dir / "betvision_backend"
    frontend_dir = base_dir / "betvision_frontend"
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return False
    
    # Install Python dependencies if needed
    print("\n📦 Checking Python dependencies...")
    try:
        import django, requests, selenium, flask
        print("✅ Python dependencies found")
    except ImportError as e:
        print(f"⚠️ Missing Python dependency: {e}")
        print("📥 Installing Python dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "django", "djangorestframework", "django-cors-headers", 
            "pillow", "requests", "selenium", "flask", "flask-cors", 
            "beautifulsoup4", "webdriver-manager"
        ])
    
    # Check if React dependencies are installed
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        if not install_react_dependencies(frontend_dir):
            return False
    else:
        print("✅ React dependencies found")
    
    # Check ports
    print("\n🔍 Checking ports...")
    ports = {
        3000: "React Frontend",
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
    
    try:
        # Run migrations
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
        "Django Backend API", 
        f"{sys.executable} manage.py runserver 0.0.0.0:8000",
        cwd=backend_dir
    ))
    
    # Wait a moment for Django to start
    time.sleep(3)
    
    # 2. React Frontend (Port 3000)
    services.append(run_service(
        "React Frontend",
        "npm start",
        cwd=frontend_dir,
        shell=True
    ))
    
    # 3. Real-time Sports System (Port 5001) - Optional
    real_time_script = base_dir / "real_time_system.py"
    if real_time_script.exists():
        services.append(run_service(
            "Real-time Sports System",
            f"{sys.executable} real_time_system.py",
            cwd=base_dir
        ))
    
    # 4. Improved Visual Monitor (Port 5002) - Optional
    visual_monitor_script = base_dir / "improved_visual_monitor.py"
    if visual_monitor_script.exists():
        services.append(run_service(
            "Improved Visual Monitor",
            f"{sys.executable} improved_visual_monitor.py",
            cwd=base_dir
        ))
    
    # Wait for services to start
    print("\n⏳ Waiting for services to start...")
    time.sleep(8)
    
    # Display service URLs
    print("\n" + "=" * 60)
    print("🎉 BetVision Pro System is READY!")
    print("=" * 60)
    print("🌐 MAIN APPLICATION:")
    print("   📱 React Frontend:   http://localhost:3000")
    print("   🔧 Django API:       http://localhost:8000/api/")
    print("   📊 Admin Panel:      http://localhost:8000/admin/")
    print()
    print("🔧 MONITORING SERVICES:")
    if real_time_script.exists():
        print("   ⚡ Real-time System: http://localhost:5001")
    if visual_monitor_script.exists():
        print("   📸 Visual Monitor:   http://localhost:5002")
    print()
    print("📋 FEATURES AVAILABLE:")
    print("   ✅ React Frontend with Modern UI")
    print("   ✅ Django REST API Backend")
    print("   ✅ User Registration & Authentication")
    print("   ✅ Professional Dashboard")
    print("   ✅ Real-time Sports Monitoring")
    print("   ✅ Advanced Screenshot Capture")
    print("   ✅ AI-powered Predictions")
    print("   ✅ Change Detection & Alerts")
    print("   ✅ Comprehensive Analytics")
    print()
    print("🎯 QUICK START:")
    print("   1. Visit http://localhost:3000")
    print("   2. Click 'Sign Up' to create account")
    print("   3. Access dashboard to start monitoring")
    print("   4. Use 'Start Monitoring' to begin")
    print()
    print("🔧 DEVELOPMENT:")
    print("   • Frontend: React app with hot reload")
    print("   • Backend: Django API with auto-reload")
    print("   • API Docs: http://localhost:8000/api/")
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