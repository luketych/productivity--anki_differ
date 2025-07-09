#!/usr/bin/env python3

import os
import sys
import argparse
from typing import Dict, List, Tuple, Set

# Import functions from diff.py to avoid code duplication
from .diff import load_anki_export, parse_anki_export


def extract_overlapping_cards(file1: str, file2: str) -> Tuple[Dict[str, str], Dict[str, str], Set[str]]:
    """Extract cards that appear in both files.
    
    Args:
        file1: Path to first Anki export file
        file2: Path to second Anki export file
        
    Returns:
        Tuple containing:
        - Dict mapping questions to answers from file1
        - Dict mapping questions to answers from file2
        - Set of common questions
    """
    # Load and parse both files
    lines1 = load_anki_export(file1)
    lines2 = load_anki_export(file2)
    
    headers1, cards1 = parse_anki_export(lines1)
    headers2, cards2 = parse_anki_export(lines2)
    
    # Create dictionaries for fast lookup
    cards1_dict = {q: a for q, a in cards1}
    cards2_dict = {q: a for q, a in cards2}
    
    # Find common questions
    common_questions = set(cards1_dict.keys()) & set(cards2_dict.keys())
    
    print(f"File 1: {len(cards1)} cards")
    print(f"File 2: {len(cards2)} cards")
    print(f"Overlapping cards: {len(common_questions)}")
    
    return cards1_dict, cards2_dict, common_questions, headers1


def generate_overlapping_export(file1: str, file2: str, output: str) -> None:
    """Generate an export file containing only the overlapping cards from file1."""
    cards1_dict, cards2_dict, common_questions, headers = extract_overlapping_cards(file1, file2)
    
    # Write the overlapping cards (using file1 version by default)
    with open(output, 'w', encoding='utf-8') as f:
        # Write headers
        for key, value in headers.items():
            f.write(f"#{key}:{value}\n")
        
        # Write cards
        for question in common_questions:
            f.write(f"{question}\t{cards1_dict[question]}\n")
    
    print(f"Created overlapping cards export at: {output}")


def generate_selection_export(file1: str, file2: str, output_prefix: str) -> None:
    """Generate a text file listing differences between overlapping cards for manual selection."""
    cards1_dict, cards2_dict, common_questions, headers = extract_overlapping_cards(file1, file2)
    
    # Find cards with different content
    different_cards = [(q, cards1_dict[q], cards2_dict[q]) 
                     for q in common_questions 
                     if cards1_dict[q] != cards2_dict[q]]
    
    print(f"Cards with content differences: {len(different_cards)}")
    
    # Generate differences report
    diff_report_path = f"{output_prefix}_differences.txt"
    with open(diff_report_path, 'w', encoding='utf-8') as f:
        f.write(f"Differences between overlapping cards\n")
        f.write(f"=================================\n\n")
        f.write(f"Total overlapping cards: {len(common_questions)}\n")
        f.write(f"Cards with differences: {len(different_cards)}\n\n")
        
        for i, (q, a1, a2) in enumerate(different_cards):
            f.write(f"Card {i+1}:\n")
            f.write(f"Question: {q}\n")
            f.write(f"File 1 Answer: {a1}\n")
            f.write(f"File 2 Answer: {a2}\n\n")
    
    # Generate selection template
    selection_path = f"{output_prefix}_selection.txt"
    with open(selection_path, 'w', encoding='utf-8') as f:
        f.write(f"# Selection template for overlapping cards with differences\n")
        f.write(f"# Format: <card_number>,<selection>\n")
        f.write(f"# Selection can be 1 (use File 1) or 2 (use File 2)\n\n")
        
        for i in range(len(different_cards)):
            f.write(f"{i+1},1\n")
    
    print(f"Created differences report at: {diff_report_path}")
    print(f"Created selection template at: {selection_path}")
    print("\nEdit the selection template to choose which version of each card to keep.")
    print("Then run: python selective_merge.py create-merged-export ...")


def create_merged_export(file1: str, file2: str, selection_file: str, output: str) -> None:
    """Create a merged export using selections from the selection file."""
    cards1_dict, cards2_dict, common_questions, headers = extract_overlapping_cards(file1, file2)
    
    # Find cards with different content
    different_questions = {q for q in common_questions if cards1_dict[q] != cards2_dict[q]}
    
    # Load the selection file
    selections = {}
    with open(selection_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            card_num, selection = line.split(',', 1)
            card_num = int(card_num)
            selection = int(selection)
            selections[card_num] = selection
    
    # Create a list of different cards for easier indexing
    different_cards = [(q, cards1_dict[q], cards2_dict[q]) for q in different_questions]
    
    # Create the merged export
    with open(output, 'w', encoding='utf-8') as f:
        # Write headers
        for key, value in headers.items():
            f.write(f"#{key}:{value}\n")
        
        # Write cards that are identical in both exports
        for question in common_questions:
            if question not in different_questions:
                f.write(f"{question}\t{cards1_dict[question]}\n")
        
        # Write cards with selections
        for i, (q, a1, a2) in enumerate(different_cards):
            card_num = i + 1
            selection = selections.get(card_num, 1)  # Default to file 1 if not specified
            answer = a1 if selection == 1 else a2
            f.write(f"{q}\t{answer}\n")
    
    print(f"Created merged export at: {output}")
    print(f"Applied {len(selections)} selections.")


def create_final_export(file1: str, file2: str, selections: Dict[str, int], output: str) -> None:
    """Create a final export with selections and unique cards from both sources."""
    # Load and parse both files
    lines1 = load_anki_export(file1)
    lines2 = load_anki_export(file2)
    
    headers1, cards1 = parse_anki_export(lines1)
    headers2, cards2 = parse_anki_export(lines2)
    
    # Create dictionaries for fast lookup
    cards1_dict = {q: a for q, a in cards1}
    cards2_dict = {q: a for q, a in cards2}
    
    # Find common questions and unique questions
    common_questions = set(cards1_dict.keys()) & set(cards2_dict.keys())
    only_in_1 = set(cards1_dict.keys()) - set(cards2_dict.keys())
    only_in_2 = set(cards2_dict.keys()) - set(cards1_dict.keys())
    
    # Find cards with different content
    different_questions = {q for q in common_questions if cards1_dict[q] != cards2_dict[q]}
    
    # Create the final export
    with open(output, 'w', encoding='utf-8') as f:
        # Write headers
        for key, value in headers1.items():
            f.write(f"#{key}:{value}\n")
        
        # Write identical cards from both exports
        for question in common_questions:
            if question not in different_questions:
                f.write(f"{question}\t{cards1_dict[question]}\n")
        
        # Write cards with selections
        for question in different_questions:
            source = selections.get(question, 1)  # Default to file 1 if not specified
            answer = cards1_dict[question] if source == 1 else cards2_dict[question]
            f.write(f"{question}\t{answer}\n")
        
        # Write cards unique to file 1 if selected
        for question in only_in_1:
            if selections.get(f"unique1:{question}", 1) == 1:  # Default to include
                f.write(f"{question}\t{cards1_dict[question]}\n")
        
        # Write cards unique to file 2 if selected
        for question in only_in_2:
            if selections.get(f"unique2:{question}", 1) == 1:  # Default to include
                f.write(f"{question}\t{cards2_dict[question]}\n")
    
    print(f"Created final export at: {output}")
    print(f"Included {len(common_questions) - len(different_questions)} identical cards")
    print(f"Included {len(different_questions)} cards with selections")
    print(f"Included {len(only_in_1)} cards unique to file 1")
    print(f"Included {len(only_in_2)} cards unique to file 2")


def main():
    parser = argparse.ArgumentParser(description='Selective merge tool for Anki exports')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Extract overlapping cards command
    extract_parser = subparsers.add_parser('extract-overlapping', 
                                          help='Extract cards that appear in both exports')
    extract_parser.add_argument('file1', help='First Anki export file')
    extract_parser.add_argument('file2', help='Second Anki export file')
    extract_parser.add_argument('output', help='Output file path')
    
    # Generate selection template command
    selection_parser = subparsers.add_parser('generate-selection', 
                                           help='Generate selection template for different cards')
    selection_parser.add_argument('file1', help='First Anki export file')
    selection_parser.add_argument('file2', help='Second Anki export file')
    selection_parser.add_argument('output_prefix', help='Output file prefix')
    
    # Create merged export command
    merge_parser = subparsers.add_parser('create-merged-export', 
                                       help='Create merged export using selections')
    merge_parser.add_argument('file1', help='First Anki export file')
    merge_parser.add_argument('file2', help='Second Anki export file')
    merge_parser.add_argument('selection_file', help='Selection file')
    merge_parser.add_argument('output', help='Output file path')
    
    # Parse args and call the appropriate function
    args = parser.parse_args()
    
    if args.command == 'extract-overlapping':
        generate_overlapping_export(args.file1, args.file2, args.output)
    elif args.command == 'generate-selection':
        generate_selection_export(args.file1, args.file2, args.output_prefix)
    elif args.command == 'create-merged-export':
        create_merged_export(args.file1, args.file2, args.selection_file, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
