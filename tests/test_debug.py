#!/usr/bin/env python3

import json
import os

# Load the comparison data
data_file = '/Users/luketych/Dev/_productivity/anki_differ/src/data/comparison_data.json'

if os.path.exists(data_file):
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print("=== MILESTONE 1 DIAGNOSTIC RESULTS ===")
    print(f"Data file exists: YES ({os.path.getsize(data_file)} bytes)")
    print(f"Data keys: {list(data.keys())}")
    
    # Check card counts
    card_counts = {
        'different_cards': len(data.get('different_cards', [])),
        'identical_cards': len(data.get('identical_cards', [])),
        'unique_file1': len(data.get('unique_file1', [])),
        'unique_file2': len(data.get('unique_file2', []))
    }
    print(f"Card counts: {card_counts}")
    
    # Check stats
    stats = data.get('stats', {})
    print(f"Stats: {stats}")
    
    # Verify data integrity
    print("\n=== DATA INTEGRITY CHECK ===")
    total_expected = stats.get('identical', 0) + stats.get('different', 0) + stats.get('only_file1', 0) + stats.get('only_file2', 0)
    total_actual = sum(card_counts.values())
    print(f"Expected total cards: {total_expected}")
    print(f"Actual total cards: {total_actual}")
    print(f"Data integrity: {'OK' if total_expected == total_actual else 'MISMATCH'}")
    
    # Sample cards
    print("\n=== SAMPLE CARDS ===")
    for card_type in ['different_cards', 'identical_cards', 'unique_file1', 'unique_file2']:
        cards = data.get(card_type, [])
        if cards:
            sample = cards[0]
            print(f"{card_type} sample:")
            print(f"  Question: {sample.get('question', 'N/A')[:50]}...")
            print(f"  Answer: {str(sample.get('answer', sample.get('file1_answer', 'N/A')))[:50]}...")
    
    print("\n=== LIKELY ISSUE HYPOTHESIS ===")
    if total_expected == total_actual and all(card_counts.values()):
        print("DATA IS VALID - Issue is likely in frontend template rendering or JavaScript")
        print("Recommended next steps:")
        print("1. Check if template loops are executing")
        print("2. Check if JavaScript data object is populated")
        print("3. Check if pagination is hiding cards")
    else:
        print("DATA ISSUE DETECTED - Backend problem")
        
else:
    print("=== MILESTONE 1 DIAGNOSTIC RESULTS ===")
    print("Data file does NOT exist - Backend issue")