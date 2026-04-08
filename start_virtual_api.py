#!/usr/bin/env python3
"""
One-click launcher for the Virtual Sports Prediction API
"""
import subprocess, sys, os

REQUIRED = ["flask", "flask_cors", "requests", "playwright"]

def install_missing():
    for pkg in REQUIRED:
        try:
            __import__(pkg)
        except ImportError:
            pip_name = pkg.replace("_", "-")
            print(f"Installing {pip_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

    # Install playwright browsers if needed
    try:
        import subprocess as sp
        sp.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)
    except Exception:
        pass

if __name__ == "__main__":
    install_missing()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("\n" + "="*55)
    print("  Virtual Sports Prediction API starting...")
    print("  http://localhost:5055")
    print("="*55 + "\n")
    import virtual_api
