#!/usr/bin/env python3
"""
Quick launcher for the Virtual Sports Prediction API
Run this first, then start the React frontend.
"""
import subprocess, sys, os

def check_deps():
    missing = []
    for pkg in ["flask", "flask_cors", "requests"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg.replace("_", "-"))
    if missing:
        print(f"Installing missing packages: {missing}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

if __name__ == "__main__":
    check_deps()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Starting Virtual Sports Prediction API on http://localhost:5050")
    import virtual_sports_api
    virtual_sports_api.init_db()
    virtual_sports_api.app.run(host="0.0.0.0", port=5050, debug=False, threaded=True)
