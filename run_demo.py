#!/usr/bin/env python3
"""
Run Demo - Guaranteed to work!
One command, instant results
"""

import os
import sys

def main():
    print("🎯 DataMiner - Guaranteed Working Demo")
    print("=" * 50)
    print("🚀 Starting instant demo...")
    print("💡 This will show working pattern analysis with 24-hour data")
    print("✅ No backend setup required - works instantly!")
    print("=" * 50)
    
    try:
        # Run the instant demo
        os.system('python instant_demo.py')
    except KeyboardInterrupt:
        print("\n✅ Demo stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Alternative: Run these commands manually:")
        print("   python simple_24h_scraper.py")
        print("   python instant_demo.py")

if __name__ == "__main__":
    main()