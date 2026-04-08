#!/usr/bin/env python3
"""
DataMiner Pro - Start Autonomous Agent
Quick start script for the autonomous AI agent
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'requests', 'beautifulsoup4', 'schedule', 'sqlite3'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️ Missing packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        
        for package in missing_packages:
            if package != 'sqlite3':  # sqlite3 is built-in
                subprocess.run([sys.executable, '-m', 'pip', 'install', package])
        
        print("✅ Dependencies installed")
    else:
        print("✅ All dependencies available")

def create_sample_config():
    """Create sample configuration if not exists"""
    config_file = "agent_config.json"
    
    if not os.path.exists(config_file):
        sample_config = {
            "database_path": "autonomous_agent.db",
            "log_level": "INFO",
            "log_file": "autonomous_agent.log",
            "max_concurrent_tasks": 5,
            "retry_attempts": 3,
            "retry_delay": 60,
            "notification_settings": {
                "email_enabled": False,
                "webhook_enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "email_user": "",
                "email_password": ""
            },
            "ai_analysis": {
                "enabled": False,
                "model": "gpt-3.5-turbo",
                "api_key": ""
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(sample_config, f, indent=2)
        
        print(f"✅ Created sample config: {config_file}")
    else:
        print(f"✅ Config file exists: {config_file}")

def show_agent_info():
    """Display information about the autonomous agent"""
    print("🤖 DataMiner Pro - Autonomous AI Agent")
    print("=" * 60)
    print()
    print("🎯 FEATURES:")
    print("  ✅ 24/7 Continuous Operation")
    print("  ✅ Automatic Data Scraping")
    print("  ✅ Change Detection & Alerts")
    print("  ✅ AI-Powered Insights")
    print("  ✅ Multiple Data Categories")
    print("  ✅ Email & Webhook Notifications")
    print("  ✅ Database Persistence")
    print("  ✅ Error Handling & Retry Logic")
    print("  ✅ Cloud Deployment Ready")
    print()
    print("📊 SUPPORTED CATEGORIES:")
    print("  🏈 Sports: Live scores, betting odds, team stats")
    print("  💰 Crypto: Prices, market data, trading signals")
    print("  🌤️  Weather: Forecasts, climate data, alerts")
    print("  📰 News: Breaking news, content updates")
    print("  🏠 Real Estate: Property listings, prices")
    print("  💼 Jobs: Job listings, salary data")
    print("  🛒 E-commerce: Product prices, deals")
    print("  📈 Forex: Currency rates, trading data")
    print()
    print("🚀 DEPLOYMENT OPTIONS:")
    print("  🐳 Docker: Containerized deployment")
    print("  ☁️  AWS Lambda: Serverless functions")
    print("  🌐 Google Cloud: Cloud functions")
    print("  🔷 Azure: Azure functions")
    print("  ⏰ Cron: Traditional scheduling")
    print("  🔧 Systemd: Linux service")
    print()

def create_demo_tasks():
    """Create demonstration tasks"""
    print("📋 Creating demo tasks...")
    
    # Import the autonomous agent
    try:
        from autonomous_ai_agent import AutonomousAIAgent, ScrapingTask
        
        agent = AutonomousAIAgent()
        
        # Demo tasks
        demo_tasks = [
            ScrapingTask(
                id="demo_news",
                name="BBC News Headlines",
                url="https://www.bbc.com/news",
                category="news",
                interval_minutes=30,
                selectors={
                    "headlines": "h3",
                    "links": "a[href*='/news/']"
                }
            ),
            ScrapingTask(
                id="demo_weather",
                name="Weather Information",
                url="https://weather.com",
                category="weather",
                interval_minutes=60,
                selectors={
                    "temperature": "[data-testid='TemperatureValue']",
                    "condition": "[data-testid='WeatherCondition']"
                }
            ),
            ScrapingTask(
                id="demo_crypto",
                name="Cryptocurrency Prices",
                url="https://coinmarketcap.com",
                category="crypto",
                interval_minutes=15,
                selectors={
                    "prices": ".price___3rj7O",
                    "names": ".currency-name-container"
                }
            )
        ]
        
        for task in demo_tasks:
            agent.add_task(task)
            print(f"  ✅ Added: {task.name}")
        
        return agent
        
    except ImportError as e:
        print(f"❌ Could not import autonomous agent: {e}")
        return None

def main():
    """Main function"""
    show_agent_info()
    
    print("🔧 SETUP:")
    print("-" * 30)
    
    # Check dependencies
    check_dependencies()
    
    # Create config
    create_sample_config()
    
    # Ask user what they want to do
    print("\n🎯 What would you like to do?")
    print("  1. Start Autonomous Agent (Demo Mode)")
    print("  2. Create Docker Deployment")
    print("  3. Create Cloud Deployment")
    print("  4. View Configuration")
    print("  5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == '1':
        print("\n🚀 Starting Autonomous Agent in Demo Mode...")
        print("⚠️ This will run continuously. Press Ctrl+C to stop.")
        
        # Create demo tasks
        agent = create_demo_tasks()
        
        if agent:
            print("\n📊 Agent Status:")
            status = agent.get_status()
            print(f"  Active Tasks: {status['active_tasks']}")
            print(f"  Total Tasks: {status['total_tasks']}")
            print(f"  Status: {'Running' if status['running'] else 'Stopped'}")
            
            print("\n🎯 Starting in 3 seconds...")
            time.sleep(3)
            
            try:
                agent.start()
            except KeyboardInterrupt:
                print("\n🛑 Agent stopped by user")
        else:
            print("❌ Could not start agent")
    
    elif choice == '2':
        print("\n🐳 Creating Docker Deployment...")
        try:
            from docker_deployment import main as docker_main
            docker_main()
        except ImportError:
            print("❌ Docker deployment module not found")
    
    elif choice == '3':
        print("\n☁️ Creating Cloud Deployment...")
        try:
            from cloud_scheduler import main as cloud_main
            cloud_main()
        except ImportError:
            print("❌ Cloud scheduler module not found")
    
    elif choice == '4':
        print("\n📋 Current Configuration:")
        try:
            with open('agent_config.json', 'r') as f:
                config = json.load(f)
                print(json.dumps(config, indent=2))
        except FileNotFoundError:
            print("❌ Configuration file not found")
    
    elif choice == '5':
        print("👋 Goodbye!")
        return
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()