#!/usr/bin/env python3

import json
import subprocess
import time
import sys

def test_app():
    """Quick test to see if our fixes work"""
    print("=== QUICK TEST: Starting app and checking endpoints ===")
    
    # Start the app in background
    try:
        print("Starting Flask app...")
        proc = subprocess.Popen(['uv', 'run', 'anki-web'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(3)
        
        # Test if app is running by trying to connect to it
        import urllib.request
        try:
            # Test the select route (which should show our debugging)
            print("Testing /select route...")
            response = urllib.request.urlopen('http://127.0.0.1:5001/select')
            content = response.read().decode('utf-8')
            
            # Check if the content contains our debug logging
            if 'POST-DEFENSIVE CHECK data arrays' in content:
                print("✅ Our JavaScript fixes are present in the template")
            else:
                print("❌ Our JavaScript fixes are NOT in the rendered template")
                
            # Check if cards are being rendered in template
            if 'different-card' in content:
                print("✅ Template is rendering different-card elements")
            else:
                print("❌ Template is NOT rendering different-card elements")
                
            if 'identical-card' in content:
                print("✅ Template is rendering identical-card elements")
            else:
                print("❌ Template is NOT rendering identical-card elements")
                
            print(f"Total page content length: {len(content)} characters")
            
        except Exception as e:
            print(f"❌ Could not connect to app: {e}")
            
    except Exception as e:
        print(f"❌ Could not start app: {e}")
    finally:
        # Kill the process
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except:
            proc.kill()

if __name__ == "__main__":
    test_app()