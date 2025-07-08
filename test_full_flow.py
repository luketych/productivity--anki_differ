#!/usr/bin/env python3
"""Test the complete flow from upload to export"""

import os
import sys
import json
import tempfile
from io import BytesIO

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from anki_differ.web.app import app

def test_complete_flow():
    """Test the complete flow from upload to export"""
    print("Testing complete flow from upload to export...")
    
    # Create test files
    test_file1 = "test_file1.txt"
    test_file2 = "test_file2.txt"
    
    with app.test_client() as client:
        # Step 1: Upload files
        with open(test_file1, 'rb') as f1, open(test_file2, 'rb') as f2:
            data = {
                'file1': (f1, test_file1),
                'file2': (f2, test_file2),
                'file1_name': 'Test File 1',
                'file2_name': 'Test File 2'
            }
            
            upload_response = client.post('/upload', data=data, content_type='multipart/form-data')
            print(f"✓ Upload response status: {upload_response.status_code}")
            
            if upload_response.status_code != 302:
                print("✗ Upload failed")
                return False
            
            # Step 2: Get selection page
            response = client.get('/select')
            print(f"✓ Selection page status: {response.status_code}")
            
            if response.status_code != 200:
                print("✗ Selection page failed")
                return False
            
            # Step 3: Test all API endpoints
            api_endpoints = [
                '/api/comparison-status',
                '/api/cards/different',
                '/api/cards/identical',
                '/api/cards/unique1',
                '/api/cards/unique2'
            ]
            
            for endpoint in api_endpoints:
                api_response = client.get(endpoint)
                print(f"✓ {endpoint} status: {api_response.status_code}")
                if api_response.status_code == 200:
                    data = api_response.get_json()
                    if 'success' in data:
                        print(f"  - Success: {data['success']}")
                    if 'cards' in data:
                        print(f"  - Cards count: {len(data['cards'])}")
                    if 'count' in data:
                        print(f"  - Count: {data['count']}")
            
            # Step 4: Test export generation
            export_response = client.get('/generate_export')
            print(f"✓ Export generation status: {export_response.status_code}")
            
            if export_response.status_code == 200:
                export_content = export_response.data.decode('utf-8')
                print(f"✓ Export content length: {len(export_content)}")
                
                # Check that the export contains our test data
                if 'What is 2+2?' in export_content:
                    print("✓ Export contains 'What is 2+2?' question")
                else:
                    print("✗ Export missing 'What is 2+2?' question")
                
                if 'What is the capital of France?' in export_content:
                    print("✓ Export contains 'What is the capital of France?' question")
                else:
                    print("✗ Export missing 'What is the capital of France?' question")
                
                # Count lines in export
                lines = export_content.strip().split('\n')
                print(f"✓ Export has {len(lines)} lines")
                
                # Check that it has the proper format
                if lines[0].startswith('#separator:'):
                    print("✓ Export has proper header format")
                else:
                    print("✗ Export missing proper header format")
                
                # Save export content for inspection
                with open('test_export.txt', 'w') as f:
                    f.write(export_content)
                print("✓ Export content saved to test_export.txt")
            
            # Step 5: Test reset functionality
            reset_response = client.get('/reset')
            print(f"✓ Reset status: {reset_response.status_code}")
            
            # Step 6: Verify reset worked
            post_reset_response = client.get('/select')
            print(f"✓ Post-reset selection page status: {post_reset_response.status_code}")
            
            if post_reset_response.status_code == 302:
                print("✓ Reset worked - redirected to index")
            else:
                print("✗ Reset failed - should have redirected to index")
            
            return True

if __name__ == '__main__':
    success = test_complete_flow()
    print(f"\nTest complete - {'SUCCESS' if success else 'FAILED'}")