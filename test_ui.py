#!/usr/bin/env python3
"""Test script to verify UI tabs are working correctly"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web_app import app
import json

# Load test data
data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
with open(data_file, 'r') as f:
    data = json.load(f)

print("=== Data Statistics ===")
print(f"Identical cards: {data['stats']['identical']}")
print(f"Different cards: {data['stats']['different']}")
print(f"Unique to file1: {data['stats']['only_file1']}")
print(f"Unique to file2: {data['stats']['only_file2']}")

# Test the app routes
with app.test_client() as client:
    # Test select page
    response = client.get('/select')
    assert response.status_code == 200
    
    html = response.data.decode('utf-8')
    
    # Check all tabs are present
    assert 'id="different-tab"' in html
    assert 'id="identical-tab"' in html
    assert 'id="unique1-tab"' in html
    assert 'id="unique2-tab"' in html
    
    # Check all tab panes are present
    assert 'id="different"' in html
    assert 'id="identical"' in html
    assert 'id="unique1"' in html
    assert 'id="unique2"' in html
    
    # Check cards are rendered
    assert 'class="anki-card different-card"' in html
    assert 'class="anki-card identical-card"' in html
    assert 'class="anki-card unique-card unique1-card"' in html
    assert 'class="anki-card unique-card unique2-card"' in html
    
    # Count cards
    different_count = html.count('class="anki-card different-card"')
    identical_count = html.count('class="anki-card identical-card"')
    unique1_count = html.count('class="anki-card unique-card unique1-card"')
    unique2_count = html.count('class="anki-card unique-card unique2-card"')
    
    print("\n=== Cards Rendered in HTML ===")
    print(f"Different cards: {different_count}")
    print(f"Identical cards: {identical_count}")
    print(f"Unique1 cards: {unique1_count}")
    print(f"Unique2 cards: {unique2_count}")
    
    # Verify counts match
    assert different_count == data['stats']['different']
    assert unique1_count == data['stats']['only_file1']
    assert unique2_count == data['stats']['only_file2']
    
    print("\n✅ All tests passed! The UI should be working correctly.")
    print("\nTo test manually, run: python app.py")
    print("Then open: http://127.0.0.1:5000/select")