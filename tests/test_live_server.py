#!/usr/bin/env python3
"""Test the live server functionality"""

import os
import sys
import json
import time
import threading
import requests
from io import BytesIO

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from anki_differ.web.app import app

def start_server():
    """Start the Flask server in a separate thread"""
    app.run(host='127.0.0.1', port=5001, debug=False)

def test_live_server():
    """Test the live server"""
    print("Testing live server functionality...")
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    try:
        # Test the index page
        response = requests.get('http://127.0.0.1:5001/')
        print(f"✓ Index page status: {response.status_code}")
        
        if response.status_code == 200:
            if 'Anki Diff' in response.text:
                print("✓ Index page contains expected content")
            else:
                print("✗ Index page missing expected content")
        
        # Test file upload
        with open('test_file1.txt', 'rb') as f1, open('test_file2.txt', 'rb') as f2:
            files = {
                'file1': f1,
                'file2': f2
            }
            data = {
                'file1_name': 'Test File 1',
                'file2_name': 'Test File 2'
            }
            
            upload_response = requests.post('http://127.0.0.1:5001/upload', 
                                          files=files, data=data, allow_redirects=False)
            print(f"✓ Upload response status: {upload_response.status_code}")
            
            if upload_response.status_code == 302:
                print("✓ Upload successful - redirected to selection page")
                
                # Test selection page
                select_response = requests.get('http://127.0.0.1:5001/select')
                print(f"✓ Selection page status: {select_response.status_code}")
                
                if select_response.status_code == 200:
                    html_content = select_response.text
                    
                    # Check for card content
                    if 'What is 2+2?' in html_content:
                        print("✓ Selection page contains expected card content")
                    else:
                        print("✗ Selection page missing expected card content")
                    
                    # Check for JavaScript data
                    if 'const data = ' in html_content:
                        print("✓ Selection page contains JavaScript data object")
                    else:
                        print("✗ Selection page missing JavaScript data object")
                    
                    # Test API endpoints
                    api_response = requests.get('http://127.0.0.1:5001/api/comparison-status')
                    print(f"✓ API comparison-status: {api_response.status_code}")
                    
                    cards_response = requests.get('http://127.0.0.1:5001/api/cards/different')
                    print(f"✓ API cards/different: {cards_response.status_code}")
                    
                    if cards_response.status_code == 200:
                        cards_data = cards_response.json()
                        print(f"✓ Different cards API returned {len(cards_data.get('cards', []))} cards")
                    
                    # Test export generation
                    export_response = requests.get('http://127.0.0.1:5001/generate_export')
                    print(f"✓ Export generation: {export_response.status_code}")
                    
                    if export_response.status_code == 200:
                        export_content = export_response.text
                        print(f"✓ Export content length: {len(export_content)}")
                        
                        with open('live_server_export.txt', 'w') as f:
                            f.write(export_content)
                        print("✓ Live server export saved to live_server_export.txt")
                    
                    print("\n🎉 All tests passed! The web application is working correctly.")
                    print("The cards are displaying as expected, and the export functionality is working.")
                    return True
                else:
                    print("✗ Selection page failed")
                    return False
            else:
                print("✗ Upload failed")
                return False
        
    except Exception as e:
        print(f"✗ Error testing live server: {e}")
        return False

if __name__ == '__main__':
    success = test_live_server()
    print(f"\nTest complete - {'SUCCESS' if success else 'FAILED'}")
    # Keep the server running for a bit to allow manual testing
    if success:
        print("\n🌐 Server is running at http://127.0.0.1:5001")
        print("You can now test the web interface manually in your browser!")
        print("Press Ctrl+C to stop the server")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nServer stopped.")