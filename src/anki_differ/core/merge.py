#!/usr/bin/env python3

import os
import sys
import argparse
from typing import Dict, List, Tuple, Set


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


def create_merged_export(file1_path: str, file2_path: str, output_path: str, conflict_resolution: str = "prefer_file1") -> None:
    """Create a merged Anki export file from two input files.
    
    Args:
        file1_path: Path to the first Anki export file
        file2_path: Path to the second Anki export file
        output_path: Path where the merged export will be saved
        conflict_resolution: How to resolve conflicts ('prefer_file1', 'prefer_file2', 'manual')
    """
    print(f"Merging {file1_path} and {file2_path} into {output_path}...")
    
    # Load and parse both files
    lines1 = load_anki_export(file1_path)
    lines2 = load_anki_export(file2_path)
    
    headers1, cards1 = parse_anki_export(lines1)
    headers2, cards2 = parse_anki_export(lines2)
    
    print(f"File 1: {len(cards1)} cards")
    print(f"File 2: {len(cards2)} cards")
    
    # Create dictionaries for faster lookup
    cards1_dict = {q: a for q, a in cards1}
    cards2_dict = {q: a for q, a in cards2}
    
    # Find common questions and unique questions
    common_questions = set(cards1_dict.keys()) & set(cards2_dict.keys())
    only_in_1 = set(cards1_dict.keys()) - set(cards2_dict.keys())
    only_in_2 = set(cards2_dict.keys()) - set(cards1_dict.keys())
    
    # Find conflicts (same question, different answer)
    conflicts = [q for q in common_questions if cards1_dict[q] != cards2_dict[q]]
    
    print(f"Common cards: {len(common_questions)}")
    print(f"Cards only in file 1: {len(only_in_1)}")
    print(f"Cards only in file 2: {len(only_in_2)}")
    print(f"Conflicts (same question, different answer): {len(conflicts)}")
    
    # Create the merged cards list
    merged_cards = []
    
    # Add all cards from file 1 that aren't in conflicts
    for q in cards1_dict:
        if q not in conflicts:
            merged_cards.append((q, cards1_dict[q]))
    
    # Add all cards from file 2 that are only in file 2
    for q in only_in_2:
        merged_cards.append((q, cards2_dict[q]))
    
    # Resolve conflicts
    conflict_resolutions = {}
    for i, q in enumerate(conflicts):
        print(f"\nConflict {i+1}/{len(conflicts)}:")
        print(f"Question: {q[:100]}..." if len(q) > 100 else f"Question: {q}")
        print(f"File 1 Answer: {cards1_dict[q][:100]}..." if len(cards1_dict[q]) > 100 else f"File 1 Answer: {cards1_dict[q]}")
        print(f"File 2 Answer: {cards2_dict[q][:100]}..." if len(cards2_dict[q]) > 100 else f"File 2 Answer: {cards2_dict[q]}")
        
        if conflict_resolution == "prefer_file1":
            merged_cards.append((q, cards1_dict[q]))
            conflict_resolutions[q] = "file1"
        elif conflict_resolution == "prefer_file2":
            merged_cards.append((q, cards2_dict[q]))
            conflict_resolutions[q] = "file2"
        elif conflict_resolution == "manual":
            choice = input("Choose (1 for File 1, 2 for File 2, B for both as separate cards): ").strip().upper()
            if choice == "1":
                merged_cards.append((q, cards1_dict[q]))
                conflict_resolutions[q] = "file1"
            elif choice == "2":
                merged_cards.append((q, cards2_dict[q]))
                conflict_resolutions[q] = "file2"
            elif choice == "B":
                # Add both as separate cards by slightly modifying the question
                merged_cards.append((q, cards1_dict[q]))
                merged_cards.append((q + " (alt)", cards2_dict[q]))
                conflict_resolutions[q] = "both"
            else:
                print("Invalid choice. Using File 1 answer as default.")
                merged_cards.append((q, cards1_dict[q]))
                conflict_resolutions[q] = "file1"
    
    # Write the merged export
    with open(output_path, 'w', encoding='utf-8') as f:
        # Write headers (using headers from file 1 as default)
        for key, value in headers1.items():
            f.write(f"#{key}:{value}\n")
        
        # Write cards
        for q, a in merged_cards:
            f.write(f"{q}\t{a}\n")
    
    print(f"\nMerged export created with {len(merged_cards)} cards.")
    print(f"Output saved to {output_path}")
    
    # Generate a report
    report_path = output_path + ".report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("Anki Export Merge Report\n")
        f.write("======================\n\n")
        f.write(f"File 1: {file1_path}\n")
        f.write(f"File 2: {file2_path}\n")
        f.write(f"Output: {output_path}\n\n")
        
        f.write(f"File 1 cards: {len(cards1)}\n")
        f.write(f"File 2 cards: {len(cards2)}\n")
        f.write(f"Merged cards: {len(merged_cards)}\n\n")
        
        f.write(f"Common cards: {len(common_questions)}\n")
        f.write(f"Cards only in file 1: {len(only_in_1)}\n")
        f.write(f"Cards only in file 2: {len(only_in_2)}\n")
        f.write(f"Conflicts resolved: {len(conflicts)}\n\n")
        
        f.write("Conflict Resolutions:\n")
        for i, q in enumerate(conflicts):
            f.write(f"Conflict {i+1}: {conflict_resolutions[q]}\n")
            f.write(f"Question: {q[:100]}..." if len(q) > 100 else f"Question: {q}\n")
            f.write(f"File 1 Answer: {cards1_dict[q][:100]}...\n" if len(cards1_dict[q]) > 100 else f"File 1 Answer: {cards1_dict[q]}\n")
            f.write(f"File 2 Answer: {cards2_dict[q][:100]}...\n\n" if len(cards2_dict[q]) > 100 else f"File 2 Answer: {cards2_dict[q]}\n\n")
    
    print(f"Merge report saved to {report_path}")


def main():
    parser = argparse.ArgumentParser(description='Merge two Anki export files.')
    parser.add_argument('file1', help='First Anki export file')
    parser.add_argument('file2', help='Second Anki export file')
    parser.add_argument('--output', '-o', default='merged_export.txt', 
                        help='Output file path (default: merged_export.txt)')
    parser.add_argument('--conflict', '-c', default='prefer_file1', 
                        choices=['prefer_file1', 'prefer_file2', 'manual'],
                        help='Conflict resolution strategy')
    
    args = parser.parse_args()
    
    create_merged_export(args.file1, args.file2, args.output, args.conflict)


if __name__ == "__main__":
    main()
