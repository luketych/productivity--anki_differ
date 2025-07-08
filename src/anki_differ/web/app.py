#!/usr/bin/env python3

import os
import sys
import json
from typing import Dict, List, Tuple, Set
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__, template_folder="../../../templates")
app.config['SECRET_KEY'] = 'anki-diff-tool-secret-key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../src/uploads')
app.config['DATA_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../src/data')

# Create directories if they don't exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['DATA_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)


def load_anki_export(file_path: str) -> List[str]:
    """Load an Anki export file and return its lines."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()


def parse_anki_export(lines: List[str]) -> Tuple[Dict[str, str], List[Tuple[str, str]]]:
    """Parse an Anki export into headers and card content."""
    headers = {}
    cards = []
    
    # Track multi-line content in case of malformed input
    current_line = ""
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('#'):
            # Parse header line
            key, value = line[1:].split(':', 1)
            headers[key] = value
        elif '\t' in line:
            # This is a complete card with tab separator
            question, answer = line.split('\t', 1)
            cards.append((question, answer))
            current_line = ""
        elif current_line:
            # This appears to be a continuation of a malformed line
            current_line += "\n" + line
            # Check if it now contains a tab
            if '\t' in current_line:
                question, answer = current_line.split('\t', 1)
                cards.append((question, answer))
                current_line = ""
        else:
            # This might be a malformed line that continues on next line
            current_line = line
            
    return headers, cards


def compare_exports(file1_path: str, file2_path: str) -> Dict:
    """Compare two Anki exports and return structured data about their differences."""
    # Load and parse both files
    lines1 = load_anki_export(file1_path)
    lines2 = load_anki_export(file2_path)
    
    headers1, cards1 = parse_anki_export(lines1)
    headers2, cards2 = parse_anki_export(lines2)
    
    # Create dictionaries for faster lookup
    cards1_dict = {q: a for q, a in cards1}
    cards2_dict = {q: a for q, a in cards2}
    
    # Find common questions, unique questions, and differences
    common_questions = set(cards1_dict.keys()) & set(cards2_dict.keys())
    only_in_1 = list(set(cards1_dict.keys()) - set(cards2_dict.keys()))
    only_in_2 = list(set(cards2_dict.keys()) - set(cards1_dict.keys()))
    
    # Extract identical and different overlapping cards
    identical_cards = []
    different_cards = []
    
    for q in common_questions:
        if cards1_dict[q] == cards2_dict[q]:
            identical_cards.append({
                "question": q,
                "answer": cards1_dict[q],
                "selected": "file1"  # Default to file1 for identical cards
            })
        else:
            different_cards.append({
                "question": q,
                "file1_answer": cards1_dict[q],
                "file2_answer": cards2_dict[q],
                "selected": "file1"  # Default to file1
            })
    
    # Prepare unique cards
    unique_file1 = [{
        "question": q,
        "answer": cards1_dict[q],
        "selected": True  # Default to include
    } for q in only_in_1]
    
    unique_file2 = [{
        "question": q,
        "answer": cards2_dict[q],
        "selected": True  # Default to include
    } for q in only_in_2]
    
    # Sort all lists by question for consistency
    identical_cards.sort(key=lambda x: x["question"])
    different_cards.sort(key=lambda x: x["question"])
    unique_file1.sort(key=lambda x: x["question"])
    unique_file2.sort(key=lambda x: x["question"])
    
    return {
        "headers": headers1,  # Use headers from file 1 by default
        "identical_cards": identical_cards,
        "different_cards": different_cards,
        "unique_file1": unique_file1,
        "unique_file2": unique_file2,
        "stats": {
            "file1_total": len(cards1),
            "file2_total": len(cards2),
            "identical": len(identical_cards),
            "different": len(different_cards),
            "only_file1": len(unique_file1),
            "only_file2": len(unique_file2)
        }
    }


def generate_anki_export(data: Dict, output_path: str) -> None:
    """Generate an Anki export file from the provided data."""
    with open(output_path, 'w', encoding='utf-8') as f:
        # Write headers
        for key, value in data["headers"].items():
            f.write(f"#{key}:{value}\n")
        
        # Write identical cards
        for card in data["identical_cards"]:
            f.write(f"{card['question']}\t{card['answer']}\n")
        
        # Write selected version of different cards
        for card in data["different_cards"]:
            answer = card["file1_answer"] if card["selected"] == "file1" else card["file2_answer"]
            f.write(f"{card['question']}\t{answer}\n")
        
        # Write selected unique cards from file 1
        for card in data["unique_file1"]:
            if card["selected"]:
                f.write(f"{card['question']}\t{card['answer']}\n")
        
        # Write selected unique cards from file 2
        for card in data["unique_file2"]:
            if card["selected"]:
                f.write(f"{card['question']}\t{card['answer']}\n")


# Routes
@app.route('/')
def index():
    # Check if we have processed data
    data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
    if os.path.exists(data_file):
        return redirect(url_for('select_cards'))
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({'error': 'Both files are required'}), 400
    
    file1 = request.files['file1']
    file2 = request.files['file2']
    file1_name = request.form.get('file1_name', 'macOS Export')
    file2_name = request.form.get('file2_name', 'Android Export')
    
    if file1.filename == '' or file2.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    file1_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file1.filename))
    file2_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file2.filename))
    
    file1.save(file1_path)
    file2.save(file2_path)
    
    # Compare the files
    comparison_data = compare_exports(file1_path, file2_path)
    comparison_data['file1_name'] = file1_name
    comparison_data['file2_name'] = file2_name
    comparison_data['file1_path'] = file1_path
    comparison_data['file2_path'] = file2_path
    
    # Save the data for later
    with open(os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json'), 'w') as f:
        json.dump(comparison_data, f, indent=2)
    
    return redirect(url_for('select_cards'))


# Removed old /select route - now using API-driven approach
@app.route('/select')
def select_cards():
    """Main card selection interface - API-driven"""
    data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
    if not os.path.exists(data_file):
        return redirect(url_for('index'))
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Only pass metadata to template, cards loaded via API
    template_data = {
        'stats': data.get('stats', {}),
        'file1_name': data.get('file1_name', 'File 1'),
        'file2_name': data.get('file2_name', 'File 2'),
        'headers': data.get('headers', {})
    }
    
    return render_template('select.html', data=template_data)


@app.route('/select-new')
def select_cards_new():
    """Enhanced UI with comprehensive debugging and testing features"""
    data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
    if not os.path.exists(data_file):
        return redirect(url_for('index'))
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Only pass metadata to template, cards loaded via API
    template_data = {
        'stats': data.get('stats', {}),
        'file1_name': data.get('file1_name', 'File 1'),
        'file2_name': data.get('file2_name', 'File 2'),
        'headers': data.get('headers', {})
    }
    
    return render_template('select_new.html', data=template_data)


@app.route('/select-api-debug')
def select_cards_api_debug():
    """API-driven UI for debugging tab content loading issues"""
    data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
    if not os.path.exists(data_file):
        return redirect(url_for('index'))
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Debug logging
    print("\n=== DEBUG: select (API-driven) route ===")
    print(f"Data keys: {list(data.keys())}")
    print(f"Different cards count: {len(data.get('different_cards', []))}")
    print(f"Identical cards count: {len(data.get('identical_cards', []))}")
    print(f"Unique file1 count: {len(data.get('unique_file1', []))}")
    print(f"Unique file2 count: {len(data.get('unique_file2', []))}")
    print(f"Stats: {data.get('stats', {})}")
    print("=== END DEBUG ===\n")
    
    # Only pass metadata to template, cards loaded via API
    template_data = {
        'stats': data.get('stats', {}),
        'file1_name': data.get('file1_name', 'File 1'),
        'file2_name': data.get('file2_name', 'File 2'),
        'headers': data.get('headers', {})
    }
    
    return render_template('select.html', data=template_data)


@app.route('/api/cards/<card_type>')
def get_cards_by_type(card_type):
    """API endpoint to fetch cards by type"""
    data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
    if not os.path.exists(data_file):
        return jsonify({'error': 'No comparison data found'}), 404
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Map card types to data keys
    card_mapping = {
        'different': 'different_cards',
        'identical': 'identical_cards', 
        'unique1': 'unique_file1',
        'unique2': 'unique_file2'
    }
    
    if card_type not in card_mapping:
        return jsonify({'error': f'Invalid card type: {card_type}'}), 400
    
    cards = data.get(card_mapping[card_type], [])
    
    return jsonify({
        'success': True,
        'cards': cards,
        'count': len(cards),
        'file1_name': data.get('file1_name', 'File 1'),
        'file2_name': data.get('file2_name', 'File 2')
    })


@app.route('/api/comparison-status')
def get_comparison_status():
    """Get overall comparison status and metadata"""
    data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
    if not os.path.exists(data_file):
        return jsonify({'error': 'No comparison data found'}), 404
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Return full debug information
    return jsonify({
        'success': True,
        'file_info': {
            'file1_name': data.get('file1_name', 'Unknown'),
            'file2_name': data.get('file2_name', 'Unknown'),
            'file1_path': data.get('file1_path', 'Unknown'),
            'file2_path': data.get('file2_path', 'Unknown')
        },
        'stats': data.get('stats', {}),
        'headers': data.get('headers', {}),
        'data_keys': list(data.keys()),
        'card_counts': {
            'different_cards': len(data.get('different_cards', [])),
            'identical_cards': len(data.get('identical_cards', [])),
            'unique_file1': len(data.get('unique_file1', [])),
            'unique_file2': len(data.get('unique_file2', []))
        },
        'file_timestamp': os.path.getmtime(data_file)
    })


@app.route('/debug/select-minimal')
def debug_select_minimal():
    """Test minimal select page without complex JavaScript"""
    data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
    if not os.path.exists(data_file):
        return "<h1>No comparison data found</h1><p>Please upload files first.</p>"
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print("\n=== DEBUG: Minimal select test ===")
    print(f"Different cards: {len(data.get('different_cards', []))}")
    print(f"Identical cards: {len(data.get('identical_cards', []))}")
    print("=== END DEBUG ===\n")
    
    return render_template('select_minimal.html', data=data)


@app.route('/debug/template-test')
def debug_template_test():
    """Test template data accessibility with simple debug template"""
    data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
    if not os.path.exists(data_file):
        return "<h1>No comparison data found</h1><p>Please upload files first.</p>"
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print("\n=== DEBUG: Template test route ===")
    print(f"Passing data with keys: {list(data.keys())}")
    print(f"Different cards: {len(data.get('different_cards', []))}")
    print(f"Identical cards: {len(data.get('identical_cards', []))}")
    print("=== END DEBUG ===\n")
    
    return render_template('debug_template.html', data=data)


@app.route('/debug/card-loading')
def debug_card_loading():
    """Debug route to test card loading without complex UI"""
    data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
    if not os.path.exists(data_file):
        return "<h1>No comparison data found</h1><p>Please upload files first.</p>"
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Create simple HTML to test data accessibility
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Card Loading Debug</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .debug-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
            .card-sample { background: #f9f9f9; padding: 10px; margin: 5px 0; }
            pre { background: #f5f5f5; padding: 10px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>Card Loading Debug Information</h1>
        
        <div class="debug-section">
            <h2>Data Structure</h2>
            <p><strong>Data Keys:</strong> {data_keys}</p>
            <p><strong>File1 Name:</strong> {file1_name}</p>
            <p><strong>File2 Name:</strong> {file2_name}</p>
        </div>
        
        <div class="debug-section">
            <h2>Card Counts</h2>
            <p><strong>Different Cards:</strong> {different_count}</p>
            <p><strong>Identical Cards:</strong> {identical_count}</p>
            <p><strong>Unique File1:</strong> {unique1_count}</p>
            <p><strong>Unique File2:</strong> {unique2_count}</p>
        </div>
        
        <div class="debug-section">
            <h2>Stats Object</h2>
            <pre>{stats}</pre>
        </div>
        
        <div class="debug-section">
            <h2>Sample Cards</h2>
            {card_samples}
        </div>
        
        <div class="debug-section">
            <h2>JavaScript Data Test</h2>
            <div id="js-test-results"></div>
            <script>
                const data = {data_json};
                
                console.log('DEBUG: JavaScript data object:', data);
                
                const results = document.getElementById('js-test-results');
                results.innerHTML = `
                    <p><strong>JS can access data:</strong> ${{data ? 'Yes' : 'No'}}</p>
                    <p><strong>JS different_cards:</strong> ${{data.different_cards ? data.different_cards.length : 'undefined'}}</p>
                    <p><strong>JS identical_cards:</strong> ${{data.identical_cards ? data.identical_cards.length : 'undefined'}}</p>
                    <p><strong>JS unique_file1:</strong> ${{data.unique_file1 ? data.unique_file1.length : 'undefined'}}</p>
                    <p><strong>JS unique_file2:</strong> ${{data.unique_file2 ? data.unique_file2.length : 'undefined'}}</p>
                `;
            </script>
        </div>
    </body>
    </html>
    """.format(
        data_keys=list(data.keys()),
        file1_name=data.get('file1_name', 'N/A'),
        file2_name=data.get('file2_name', 'N/A'),
        different_count=len(data.get('different_cards', [])),
        identical_count=len(data.get('identical_cards', [])),
        unique1_count=len(data.get('unique_file1', [])),
        unique2_count=len(data.get('unique_file2', [])),
        stats=json.dumps(data.get('stats', {}), indent=2),
        card_samples=generate_card_samples(data),
        data_json=json.dumps(data).replace('</script>', '<\\/script>')
    )
    
    return html


def generate_card_samples(data):
    """Generate HTML samples of cards for debugging"""
    samples = []
    
    for card_type in ['different_cards', 'identical_cards', 'unique_file1', 'unique_file2']:
        cards = data.get(card_type, [])
        if cards:
            card = cards[0]
            samples.append(f"""
                <div class="card-sample">
                    <h4>{card_type}</h4>
                    <p><strong>Question:</strong> {card.get('question', 'N/A')[:100]}...</p>
                    <p><strong>Answer:</strong> {str(card.get('answer', card.get('file1_answer', 'N/A')))[:100]}...</p>
                </div>
            """)
    
    return ''.join(samples)


@app.route('/save_selections', methods=['POST'])
def save_selections():
    data = request.get_json()
    
    # Save the updated data
    with open(os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json'), 'w') as f:
        json.dump(data, f, indent=2)
    
    return jsonify({'status': 'success'})


@app.route('/generate_export')
def generate_export():
    data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
    if not os.path.exists(data_file):
        return redirect(url_for('index'))
    
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    # Generate the export file
    export_file = os.path.join(app.config['DATA_FOLDER'], 'merged_export.txt')
    generate_anki_export(data, export_file)
    
    return send_file(export_file, as_attachment=True, download_name='merged_anki_export.txt')


@app.route('/reset')
def reset():
    # Remove data files
    data_file = os.path.join(app.config['DATA_FOLDER'], 'comparison_data.json')
    if os.path.exists(data_file):
        os.remove(data_file)
    
    export_file = os.path.join(app.config['DATA_FOLDER'], 'merged_export.txt')
    if os.path.exists(export_file):
        os.remove(export_file)
    
    # Clean up uploads
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
