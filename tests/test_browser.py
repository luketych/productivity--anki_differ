#!/usr/bin/env python3
"""Test the web interface by directly accessing the HTML content"""

import os
import sys
import json
import tempfile
from io import BytesIO

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from anki_differ.web.app import app

def test_selection_page():
    """Test the selection page HTML generation"""
    print("Testing selection page HTML generation...")
    
    # Create test files
    test_file1 = "test_file1.txt"
    test_file2 = "test_file2.txt"
    
    with app.test_client() as client:
        # First upload files
        with open(test_file1, 'rb') as f1, open(test_file2, 'rb') as f2:
            data = {
                'file1': (f1, test_file1),
                'file2': (f2, test_file2),
                'file1_name': 'Test File 1',
                'file2_name': 'Test File 2'
            }
            
            upload_response = client.post('/upload', data=data, content_type='multipart/form-data')
            print(f"Upload response status: {upload_response.status_code}")
            
            if upload_response.status_code == 302:
                # Now test the selection page
                response = client.get('/select')
                print(f"Selection page status: {response.status_code}")
                print(f"Selection page content length: {len(response.data)}")
                
                # Save the HTML content to a file for inspection
                html_content = response.data.decode('utf-8')
                with open('selection_page_debug.html', 'w') as f:
                    f.write(html_content)
                
                print("Selection page HTML saved to selection_page_debug.html")
                
                # Let's look for specific content in the HTML
                print("\nChecking for card content in HTML:")
                
                # Look for the different cards content
                if 'What is 2+2?' in html_content:
                    print("✓ Found 'What is 2+2?' question in HTML")
                else:
                    print("✗ Missing 'What is 2+2?' question in HTML")
                
                if 'different-card' in html_content:
                    print("✓ Found 'different-card' class in HTML")
                else:
                    print("✗ Missing 'different-card' class in HTML")
                
                # Check if the data object contains cards
                if 'different_cards' in html_content:
                    print("✓ Found 'different_cards' in HTML")
                else:
                    print("✗ Missing 'different_cards' in HTML")
                    
                # Count actual card elements
                card_count = html_content.count('class="anki-card different-card"')
                print(f"Found {card_count} different-card elements in HTML")
                
                # Check the JavaScript data object
                if 'const data = ' in html_content:
                    print("✓ Found JavaScript data object")
                    # Extract the data portion
                    start = html_content.find('const data = ') + len('const data = ')
                    end = html_content.find(';', start)
                    if end > start:
                        try:
                            data_str = html_content[start:end].strip()
                            print(f"JavaScript data object: {data_str[:200]}...")
                        except:
                            print("Could not extract JavaScript data object")
                else:
                    print("✗ Missing JavaScript data object")

if __name__ == '__main__':
    test_selection_page()