#!/usr/bin/env python3
"""
BetVision Pro Backend Startup Script
Initializes Django backend with migrations and starts the server
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        print(f"🔧 Running: {command}")
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def main():
    """Main startup function"""
    print("🚀 BetVision Pro Backend Startup")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "betvision_backend"
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    print(f"📁 Working directory: {backend_dir}")
    
    # Check if Django is installed
    try:
        import django
        print(f"✅ Django {django.get_version()} found")
    except ImportError:
        print("❌ Django not installed. Installing...")
        if not run_command("pip install django djangorestframework django-cors-headers pillow"):
            print("❌ Failed to install Django dependencies")
            return False
    
    # Make migrations
    print("\n📋 Creating database migrations...")
    if not run_command("python manage.py makemigrations", cwd=backend_dir):
        print("❌ Failed to create migrations")
        return False
    
    # Run migrations
    print("\n🗄️ Running database migrations...")
    if not run_command("python manage.py migrate", cwd=backend_dir):
        print("❌ Failed to run migrations")
        return False
    
    # Create superuser (optional)
    print("\n👤 Creating superuser (optional)...")
    print("You can skip this by pressing Ctrl+C")
    try:
        subprocess.run("python manage.py createsuperuser", shell=True, cwd=backend_dir)
    except KeyboardInterrupt:
        print("\n⏭️ Skipped superuser creation")
    
    # Collect static files
    print("\n📦 Collecting static files...")
    run_command("python manage.py collectstatic --noinput", cwd=backend_dir)
    
    # Start the server
    print("\n🌐 Starting BetVision Pro Backend Server...")
    print("📡 Backend will be available at: http://localhost:8000")
    print("🎯 Landing page: http://localhost:8000")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("🔧 Admin panel: http://localhost:8000/admin")
    print("📚 API docs: http://localhost:8000/api/")
    print("\n" + "=" * 50)
    print("🎉 BetVision Pro Backend is ready!")
    print("=" * 50)
    
    try:
        # Start Django development server
        subprocess.run("python manage.py runserver 0.0.0.0:8000", shell=True, cwd=backend_dir)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)