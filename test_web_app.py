#!/usr/bin/env python3
"""Test script to verify web app functionality"""

import os
import sys
import json
import tempfile
from io import BytesIO

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from anki_differ.web.app import app, compare_exports

def test_upload_functionality():
    """Test the file upload and comparison functionality"""
    print("Testing upload functionality...")
    
    # Create test files
    test_file1 = "test_file1.txt"
    test_file2 = "test_file2.txt"
    
    with app.test_client() as client:
        # Test the upload endpoint
        with open(test_file1, 'rb') as f1, open(test_file2, 'rb') as f2:
            data = {
                'file1': (f1, test_file1),
                'file2': (f2, test_file2),
                'file1_name': 'Test File 1',
                'file2_name': 'Test File 2'
            }
            
            response = client.post('/upload', data=data, content_type='multipart/form-data')
            print(f"Upload response status: {response.status_code}")
            print(f"Upload response headers: {response.headers}")
            
            if response.status_code == 302:
                print("Upload successful, redirected to selection page")
                
                # Check if comparison data was created
                data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
                if os.path.exists(data_file):
                    with open(data_file, 'r') as f:
                        data = json.load(f)
                        print("Comparison data created successfully:")
                        print(json.dumps(data, indent=2))
                        
                        # Test the selection page
                        response = client.get('/select')
                        print(f"Selection page status: {response.status_code}")
                        print(f"Selection page content length: {len(response.data)}")
                        
                        # Test API endpoints
                        response = client.get('/api/comparison-status')
                        print(f"API status response: {response.status_code}")
                        if response.status_code == 200:
                            api_data = response.get_json()
                            print("API response data:")
                            print(json.dumps(api_data, indent=2))
                        
                        # Test different cards API
                        response = client.get('/api/cards/different')
                        print(f"Different cards API response: {response.status_code}")
                        if response.status_code == 200:
                            cards_data = response.get_json()
                            print("Different cards data:")
                            print(json.dumps(cards_data, indent=2))
                            
                else:
                    print("ERROR: No comparison data file created")
            else:
                print(f"Upload failed: {response.data}")

def test_compare_exports_directly():
    """Test the comparison logic directly"""
    print("\nTesting comparison logic directly...")
    
    test_file1 = "test_file1.txt"
    test_file2 = "test_file2.txt"
    
    try:
        result = compare_exports(test_file1, test_file2)
        print("Direct comparison successful:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Direct comparison failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("Starting web app tests...")
    test_compare_exports_directly()
    test_upload_functionality()
    print("Tests completed.")