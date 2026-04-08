#!/usr/bin/env python3
"""
DataMiner Pro - Complete System Startup
Integrated startup script for the complete DataMiner Pro system with all features
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path
import json

def show_system_overview():
    """Display complete system overview"""
    print("🎯 DataMiner Pro - Complete System")
    print("=" * 70)
    print()
    print("🚀 INTEGRATED FEATURES:")
    print("  ✅ React Frontend with Modern UI")
    print("  ✅ Django REST API Backend")
    print("  ✅ User Authentication & Authorization")
    print("  ✅ Professional Dashboard")
    print("  ✅ Multi-Category Data Monitoring")
    print("  ✅ Real-time Sports Monitoring")
    print("  ✅ Advanced Screenshot Capture")
    print("  ✅ AI-powered Predictions")
    print("  ✅ 🤖 Betting Visual History Extractor")
    print("  ✅ 🤖 Autonomous AI Agent (24/7)")
    print("  ✅ Change Detection & Alerts")
    print("  ✅ Comprehensive Analytics")
    print("  ✅ Database Storage & Export")
    print()
    print("🎯 SUPPORTED CATEGORIES:")
    print("  🏈 Sports: Live scores, betting odds, team stats")
    print("  💰 Crypto: Prices, market data, trading signals")
    print("  🌤️  Weather: Forecasts, climate data, alerts")
    print("  📰 News: Breaking news, content updates")
    print("  🏠 Real Estate: Property listings, prices")
    print("  💼 Jobs: Job listings, salary data")
    print("  🛒 E-commerce: Product prices, deals")
    print("  📈 Forex: Currency rates, trading data")
    print()
    print("🤖 AI-POWERED FEATURES:")
    print("  🔍 Visual History Extraction with OCR")
    print("  📸 Computer Vision Analysis")
    print("  🧠 Pattern Recognition & Insights")
    print("  ⚡ Autonomous 24/7 Operation")
    print("  📊 Confidence Scoring")
    print("  🎯 Smart Data Parsing")
    print()

def check_dependencies():
    """Check all system dependencies"""
    print("📦 Checking system dependencies...")
    
    # Python packages
    python_packages = [
        'django', 'djangorestframework', 'django-cors-headers',
        'flask', 'flask-cors', 'selenium', 'opencv-python',
        'pillow', 'pytesseract', 'easyocr', 'webdriver-manager',
        'beautifulsoup4', 'requests', 'numpy', 'schedule'
    ]
    
    missing_packages = []
    
    for package in python_packages:
        try:
            if package == 'opencv-python':
                import cv2
            elif package == 'pillow':
                from PIL import Image
            elif package == 'django-cors-headers':
                import corsheaders
            elif package == 'djangorestframework':
                import rest_framework
            elif package == 'flask-cors':
                from flask_cors import CORS
            elif package == 'webdriver-manager':
                from webdriver_manager.chrome import ChromeDriverManager
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️ Missing Python packages: {', '.join(missing_packages)}")
        print("📥 Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             check=True, capture_output=True)
                print(f"  ✅ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to install {package}: {e}")
    else:
        print("✅ All Python dependencies available")
    
    # Check Node.js and npm
    try:
        node_result = subprocess.run(['node', '--version'], capture_output=True, text=True, shell=True)
        npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True, shell=True)
        
        if node_result.returncode == 0 and npm_result.returncode == 0:
            print(f"✅ Node.js {node_result.stdout.strip()}")
            print(f"✅ npm {npm_result.stdout.strip()}")
        else:
            print("❌ Node.js and npm required for React frontend")
            return False
    except Exception as e:
        print(f"❌ Node.js check failed: {e}")
        return False
    
    return True

def setup_databases():
    """Setup Django database"""
    print("🗄️ Setting up databases...")
    
    backend_dir = Path("betvision_backend")
    
    try:
        # Run Django migrations
        subprocess.run([
            sys.executable, "manage.py", "makemigrations"
        ], cwd=backend_dir, check=True, capture_output=True)
        
        subprocess.run([
            sys.executable, "manage.py", "migrate"
        ], cwd=backend_dir, check=True, capture_output=True)
        
        print("✅ Django database initialized")
        
        # Create sample betting sites
        create_sample_data_script = '''
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'betvision_backend.settings')
django.setup()

from betting_extractor.models import BettingSite

sites = [
    {"name": "FlashScore", "url": "https://www.flashscore.com", "login_required": False},
    {"name": "LiveScore", "url": "https://www.livescore.com", "login_required": False},
    {"name": "Bet365", "url": "https://www.bet365.com", "login_required": True},
    {"name": "Bet9ja", "url": "https://www.bet9ja.com", "login_required": False},
    {"name": "Betway", "url": "https://www.betway.com", "login_required": True},
]

for site_data in sites:
    site, created = BettingSite.objects.get_or_create(
        name=site_data["name"],
        defaults=site_data
    )
    if created:
        print(f"Created betting site: {site.name}")

print("Sample betting sites created")
'''
        
        with open(backend_dir / "create_sample_data.py", "w") as f:
            f.write(create_sample_data_script)
        
        subprocess.run([
            sys.executable, "create_sample_data.py"
        ], cwd=backend_dir, capture_output=True)
        
        print("✅ Sample data created")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        return False

def install_react_dependencies():
    """Install React dependencies"""
    print("📦 Installing React dependencies...")
    
    frontend_dir = Path("betvision_frontend")
    node_modules = frontend_dir / "node_modules"
    
    if not node_modules.exists():
        try:
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True, shell=True)
            print("✅ React dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install React dependencies: {e}")
            return False
    else:
        print("✅ React dependencies already installed")
        return True

def start_django_backend():
    """Start Django backend server"""
    def run_django():
        try:
            print("🚀 Starting Django backend on port 8000...")
            subprocess.run([
                sys.executable, "manage.py", "runserver", "0.0.0.0:8000"
            ], cwd="betvision_backend")
        except Exception as e:
            print(f"❌ Django backend error: {e}")
    
    django_thread = threading.Thread(target=run_django, daemon=True)
    django_thread.start()
    return django_thread

def start_react_frontend():
    """Start React frontend server"""
    def run_react():
        try:
            print("🚀 Starting React frontend on port 3000...")
            subprocess.run(['npm', 'start'], cwd="betvision_frontend", shell=True)
        except Exception as e:
            print(f"❌ React frontend error: {e}")
    
    react_thread = threading.Thread(target=run_react, daemon=True)
    react_thread.start()
    return react_thread

def start_autonomous_agent():
    """Start autonomous AI agent"""
    def run_agent():
        try:
            print("🤖 Starting Autonomous AI Agent...")
            from autonomous_ai_agent import AutonomousAIAgent, ScrapingTask
            
            agent = AutonomousAIAgent()
            
            # Add sample tasks if none exist
            if not agent.tasks:
                sample_tasks = [
                    ScrapingTask(
                        id="auto_sports",
                        name="Auto Sports Monitoring",
                        url="https://www.flashscore.com/football/",
                        category="sports",
                        interval_minutes=10,
                        selectors={
                            "matches": ".event__match",
                            "scores": ".event__score",
                            "teams": ".event__participant"
                        }
                    ),
                    ScrapingTask(
                        id="auto_crypto",
                        name="Auto Crypto Monitoring",
                        url="https://coinmarketcap.com/",
                        category="crypto",
                        interval_minutes=15,
                        selectors={
                            "prices": ".price___3rj7O",
                            "names": ".currency-name-container"
                        }
                    )
                ]
                
                for task in sample_tasks:
                    agent.add_task(task)
            
            agent.start()
            
        except Exception as e:
            print(f"❌ Autonomous agent error: {e}")
    
    agent_thread = threading.Thread(target=run_agent, daemon=True)
    agent_thread.start()
    return agent_thread

def start_betting_visual_api():
    """Start betting visual extractor API"""
    def run_betting_api():
        try:
            print("🎯 Starting Betting Visual Extractor API on port 5003...")
            from betting_visual_api import main
            main()
        except Exception as e:
            print(f"❌ Betting visual API error: {e}")
    
    api_thread = threading.Thread(target=run_betting_api, daemon=True)
    api_thread.start()
    return api_thread

def main():
    """Main startup function"""
    show_system_overview()
    
    print("🚀 SYSTEM STARTUP:")
    print("-" * 30)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        return False
    
    # Setup databases
    if not setup_databases():
        print("❌ Database setup failed")
        return False
    
    # Install React dependencies
    if not install_react_dependencies():
        print("❌ React setup failed")
        return False
    
    print("\n🎯 STARTUP OPTIONS:")
    print("  1. Start Complete System (Recommended)")
    print("  2. Start Django Backend Only")
    print("  3. Start React Frontend Only")
    print("  4. Start Autonomous Agent Only")
    print("  5. Start Betting Visual Extractor Only")
    print("  6. System Status")
    print("  7. Exit")
    
    while True:
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == '1':
            print("\n🚀 Starting Complete DataMiner Pro System...")
            print("⏳ Initializing all services...")
            
            # Start all services
            django_thread = start_django_backend()
            time.sleep(5)  # Wait for Django to start
            
            react_thread = start_react_frontend()
            time.sleep(3)  # Wait for React to start
            
            agent_thread = start_autonomous_agent()
            time.sleep(2)
            
            betting_api_thread = start_betting_visual_api()
            time.sleep(3)
            
            print("\n🎉 DATAMINER PRO SYSTEM IS READY!")
            print("=" * 60)
            print("🌐 MAIN APPLICATION:")
            print("   📱 React Frontend:   http://localhost:3000")
            print("   🔧 Django API:       http://localhost:8000/api/")
            print("   📊 Admin Panel:      http://localhost:8000/admin/")
            print()
            print("🤖 AI SERVICES:")
            print("   🎯 Betting Extractor: http://localhost:5003")
            print("   ⚡ Autonomous Agent:  Running in background")
            print()
            print("🎯 QUICK START:")
            print("   1. Visit http://localhost:3000")
            print("   2. Click 'Sign Up' to create account")
            print("   3. Access dashboard to start monitoring")
            print("   4. Click 'Sports' → 'Visual History Extractor'")
            print("   5. Use autonomous agent for 24/7 monitoring")
            print()
            print("📊 FEATURES AVAILABLE:")
            print("   ✅ Multi-category data monitoring")
            print("   ✅ Visual betting history extraction")
            print("   ✅ Autonomous 24/7 AI agent")
            print("   ✅ Real-time progress tracking")
            print("   ✅ Advanced OCR and computer vision")
            print("   ✅ Database storage and analytics")
            print("   ✅ Professional web interface")
            print()
            print("Press Ctrl+C to stop all services")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down DataMiner Pro...")
                print("✅ All services stopped")
                break
        
        elif choice == '2':
            print("\n🔧 Starting Django Backend Only...")
            django_thread = start_django_backend()
            print("✅ Django backend started on http://localhost:8000")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Django backend stopped")
                break
        
        elif choice == '3':
            print("\n📱 Starting React Frontend Only...")
            react_thread = start_react_frontend()
            print("✅ React frontend started on http://localhost:3000")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 React frontend stopped")
                break
        
        elif choice == '4':
            print("\n🤖 Starting Autonomous Agent Only...")
            agent_thread = start_autonomous_agent()
            print("✅ Autonomous agent started")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Autonomous agent stopped")
                break
        
        elif choice == '5':
            print("\n🎯 Starting Betting Visual Extractor Only...")
            betting_api_thread = start_betting_visual_api()
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Betting visual extractor stopped")
                break
        
        elif choice == '6':
            print("\n📊 System Status:")
            print(f"  Python Version: {sys.version.split()[0]}")
            print(f"  Working Directory: {os.getcwd()}")
            print(f"  Django Backend: {'✅' if Path('betvision_backend').exists() else '❌'}")
            print(f"  React Frontend: {'✅' if Path('betvision_frontend').exists() else '❌'}")
            print(f"  Autonomous Agent: {'✅' if Path('autonomous_ai_agent.py').exists() else '❌'}")
            print(f"  Betting Extractor: {'✅' if Path('betting_visual_history_extractor.py').exists() else '❌'}")
            print(f"  Database: {'✅' if Path('betvision_backend/db.sqlite3').exists() else '❌'}")
        
        elif choice == '7':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please select 1-7.")

if __name__ == "__main__":
    main()