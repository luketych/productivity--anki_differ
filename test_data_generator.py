#!/usr/bin/env python3
"""
Test data generator for Anki diff UI testing
Creates consistent, controllable test data for debugging UI issues
"""

import json
import os
import sys

def generate_test_data():
    """Generate comprehensive test data with known quantities for each category"""
    
    # Small, controlled dataset for debugging
    test_data = {
        "headers": {
            "separator": "tab",
            "html": "true"
        },
        "file1_name": "Test File 1",
        "file2_name": "Test File 2",
        "file1_path": "/tmp/test1.txt",
        "file2_path": "/tmp/test2.txt",
        
        # 3 identical cards - easy to verify
        "identical_cards": [
            {
                "question": "What is 2 + 2?",
                "answer": "4",
                "selected": "file1"
            },
            {
                "question": "What is the capital of France?",
                "answer": "Paris",
                "selected": "file1"
            },
            {
                "question": "What color is the sky?",
                "answer": "Blue",
                "selected": "file1"
            }
        ],
        
        # 2 different cards - easy to verify
        "different_cards": [
            {
                "question": "What is the best programming language?",
                "file1_answer": "Python",
                "file2_answer": "JavaScript",
                "selected": "file1"
            },
            {
                "question": "What is the meaning of life?",
                "file1_answer": "42",
                "file2_answer": "To be happy",
                "selected": "file1"
            }
        ],
        
        # 4 unique to file1 - easy to verify
        "unique_file1": [
            {
                "question": "Python-specific question 1?",
                "answer": "Python answer 1",
                "selected": True
            },
            {
                "question": "Python-specific question 2?",
                "answer": "Python answer 2",
                "selected": True
            },
            {
                "question": "Python-specific question 3?",
                "answer": "Python answer 3",
                "selected": True
            },
            {
                "question": "Python-specific question 4?",
                "answer": "Python answer 4",
                "selected": True
            }
        ],
        
        # 5 unique to file2 - easy to verify
        "unique_file2": [
            {
                "question": "JavaScript-specific question 1?",
                "answer": "JavaScript answer 1",
                "selected": True
            },
            {
                "question": "JavaScript-specific question 2?",
                "answer": "JavaScript answer 2",
                "selected": True
            },
            {
                "question": "JavaScript-specific question 3?",
                "answer": "JavaScript answer 3",
                "selected": True
            },
            {
                "question": "JavaScript-specific question 4?",
                "answer": "JavaScript answer 4",
                "selected": True
            },
            {
                "question": "JavaScript-specific question 5?",
                "answer": "JavaScript answer 5",
                "selected": True
            }
        ],
        
        # Stats should match the above
        "stats": {
            "file1_total": 9,  # 3 identical + 2 different + 4 unique1
            "file2_total": 10, # 3 identical + 2 different + 5 unique2
            "identical": 3,
            "different": 2,
            "only_file1": 4,
            "only_file2": 5
        }
    }
    
    return test_data

def generate_large_test_data():
    """Generate larger test data for pagination testing"""
    
    base_data = generate_test_data()
    
    # Add more cards to test pagination
    for i in range(20):
        base_data["identical_cards"].append({
            "question": f"Bulk identical question {i+4}?",
            "answer": f"Bulk identical answer {i+4}",
            "selected": "file1"
        })
    
    for i in range(15):
        base_data["unique_file1"].append({
            "question": f"Bulk unique1 question {i+5}?",
            "answer": f"Bulk unique1 answer {i+5}",
            "selected": True
        })
    
    for i in range(18):
        base_data["unique_file2"].append({
            "question": f"Bulk unique2 question {i+6}?",
            "answer": f"Bulk unique2 answer {i+6}",
            "selected": True
        })
    
    # Update stats
    base_data["stats"]["identical"] = len(base_data["identical_cards"])
    base_data["stats"]["only_file1"] = len(base_data["unique_file1"])
    base_data["stats"]["only_file2"] = len(base_data["unique_file2"])
    base_data["stats"]["file1_total"] = (base_data["stats"]["identical"] + 
                                        base_data["stats"]["different"] + 
                                        base_data["stats"]["only_file1"])
    base_data["stats"]["file2_total"] = (base_data["stats"]["identical"] + 
                                        base_data["stats"]["different"] + 
                                        base_data["stats"]["only_file2"])
    
    return base_data

def save_test_data(data, filename="test_comparison_data.json"):
    """Save test data to file"""
    
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), 'src', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    file_path = os.path.join(data_dir, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Test data saved to {file_path}")
    return file_path

def validate_test_data(data):
    """Validate that test data is consistent"""
    
    print("🔍 Validating test data...")
    
    # Check required keys
    required_keys = ['identical_cards', 'different_cards', 'unique_file1', 'unique_file2', 'stats']
    for key in required_keys:
        assert key in data, f"Missing required key: {key}"
    
    # Validate stats match actual data
    assert data['stats']['identical'] == len(data['identical_cards']), "Identical count mismatch"
    assert data['stats']['different'] == len(data['different_cards']), "Different count mismatch" 
    assert data['stats']['only_file1'] == len(data['unique_file1']), "Unique file1 count mismatch"
    assert data['stats']['only_file2'] == len(data['unique_file2']), "Unique file2 count mismatch"
    
    # Validate card structure
    for card in data['identical_cards']:
        assert 'question' in card and 'answer' in card, "Invalid identical card structure"
    
    for card in data['different_cards']:
        assert all(k in card for k in ['question', 'file1_answer', 'file2_answer']), "Invalid different card structure"
    
    for card in data['unique_file1']:
        assert 'question' in card and 'answer' in card and 'selected' in card, "Invalid unique1 card structure"
    
    for card in data['unique_file2']:
        assert 'question' in card and 'answer' in card and 'selected' in card, "Invalid unique2 card structure"
    
    print("✅ Test data validation passed")
    
    # Print summary
    print("\n📊 Test Data Summary:")
    print(f"  Identical cards: {data['stats']['identical']}")
    print(f"  Different cards: {data['stats']['different']}")
    print(f"  Unique to file1: {data['stats']['only_file1']}")
    print(f"  Unique to file2: {data['stats']['only_file2']}")
    print(f"  Total file1: {data['stats']['file1_total']}")
    print(f"  Total file2: {data['stats']['file2_total']}")

if __name__ == "__main__":
    print("🚀 Generating test data for Anki diff UI...")
    
    # Generate small test data
    small_data = generate_test_data()
    validate_test_data(small_data)
    save_test_data(small_data, "small_test_data.json")
    
    # Generate large test data
    large_data = generate_large_test_data()
    validate_test_data(large_data)
    save_test_data(large_data, "large_test_data.json")
    
    # Save as the main comparison data for immediate testing
    save_test_data(small_data, "comparison_data.json")
    
    print("\n🎉 Test data generation complete!")
    print("Run the app with: python app.py")