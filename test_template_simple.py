#!/usr/bin/env python3

import json
import os
from jinja2 import Template

# Load the comparison data
data_file = '/Users/luketych/Dev/_productivity/anki_differ/src/data/comparison_data.json'

if os.path.exists(data_file):
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Simple template test
    template_str = """
    <h1>Template Test</h1>
    <p>Different cards count: {{ data.different_cards|length }}</p>
    <p>Identical cards count: {{ data.identical_cards|length }}</p>
    
    <h2>Different Cards (first 2):</h2>
    {% for card in data.different_cards[:2] %}
    <div class="card-{{ loop.index0 }}">
        <p>Question: {{ card.question[:50] }}...</p>
        <p>File1: {{ card.file1_answer[:50] }}...</p>
    </div>
    {% endfor %}
    
    <h2>Identical Cards (first 2):</h2>
    {% for card in data.identical_cards[:2] %}
    <div class="card-{{ loop.index0 }}">
        <p>Question: {{ card.question[:50] }}...</p>
        <p>Answer: {{ card.answer[:50] }}...</p>
    </div>
    {% endfor %}
    """
    
    template = Template(template_str)
    rendered = template.render(data=data)
    
    print("=== TEMPLATE RENDERING TEST ===")
    print("Template rendered successfully!")
    print(f"Output length: {len(rendered)} characters")
    print("\nRendered content (first 500 chars):")
    print(rendered[:500])
    print("\n=== Template can access data arrays ===")
    
    # Test if the loops would create any content
    different_count = len(data.get('different_cards', []))
    identical_count = len(data.get('identical_cards', []))
    
    print(f"Different cards in data: {different_count}")
    print(f"Identical cards in data: {identical_count}")
    
    if different_count > 0:
        print("✅ Template should render different cards")
    else:
        print("❌ No different cards to render")
        
    if identical_count > 0:
        print("✅ Template should render identical cards")
    else:
        print("❌ No identical cards to render")
        
else:
    print("No data file found")