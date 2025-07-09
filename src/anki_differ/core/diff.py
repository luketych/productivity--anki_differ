#!/usr/bin/env python3

import sys
import difflib
import re
import os
from typing import Dict, List, Tuple, Set, Union, Optional

# Import the new Card class
from .card import Card, SimilarityMetadata, SimilarityStatus, cards_to_tuples, tuples_to_cards


def load_anki_export(file_path: str) -> List[str]:
    """Load an Anki export file and return its lines."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()


def parse_anki_export(lines: List[str]) -> Tuple[Dict[str, str], List[Tuple[str, str]]]:
    """Parse an Anki export into headers and card content (legacy tuple format)."""
    headers, cards = parse_anki_export_cards(lines)
    return headers, cards_to_tuples(cards)


def parse_anki_export_cards(lines: List[str]) -> Tuple[Dict[str, str], List[Card]]:
    """Parse an Anki export into headers and Card objects."""
    headers = {}
    cards = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('#'):
            # Parse header line
            key, value = line[1:].split(':', 1)
            headers[key] = value
        else:
            # Parse card content
            if '\t' in line:
                question, answer = line.split('\t', 1)
                cards.append(Card(question=question, answer=answer))
            else:
                print(f"Warning: Line {i+1} doesn't contain a tab separator: {line}")
                
    return headers, cards


def find_missing_cards(cards1: List[Tuple[str, str]], cards2: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """Find cards that are in one set but not the other (legacy tuple format)."""
    cards1_objects = tuples_to_cards(cards1)
    cards2_objects = tuples_to_cards(cards2)
    
    missing_in_1, missing_in_2 = find_missing_cards_objects(cards1_objects, cards2_objects)
    
    return cards_to_tuples(missing_in_1), cards_to_tuples(missing_in_2)


def find_missing_cards_objects(cards1: List[Card], cards2: List[Card]) -> Tuple[List[Card], List[Card]]:
    """Find cards that are in one set but not the other."""
    set1 = set(card.to_tuple() for card in cards1)
    set2 = set(card.to_tuple() for card in cards2)
    
    missing_in_2 = [card for card in cards1 if card.to_tuple() not in set2]
    missing_in_1 = [card for card in cards2 if card.to_tuple() not in set1]
    
    return missing_in_1, missing_in_2


def find_content_differences(cards1: List[Tuple[str, str]], cards2: List[Tuple[str, str]]) -> List[Tuple[int, Tuple[str, str], Tuple[str, str]]]:
    """Find differences in shared cards (legacy tuple format)."""
    cards1_objects = tuples_to_cards(cards1)
    cards2_objects = tuples_to_cards(cards2)
    
    differences = find_content_differences_objects(cards1_objects, cards2_objects)
    
    # Convert back to legacy format
    result = []
    for idx, card1, card2 in differences:
        result.append((idx, card1.to_tuple(), card2.to_tuple()))
    
    return result


def find_content_differences_objects(cards1: List[Card], cards2: List[Card]) -> List[Tuple[int, Card, Card]]:
    """Find differences in shared cards."""
    differences = []
    
    # Create dictionaries with question as key for faster lookup
    cards1_dict = {card.question: card for card in cards1}
    cards2_dict = {card.question: card for card in cards2}
    
    # Find shared questions with different answers
    common_questions = set(cards1_dict.keys()) & set(cards2_dict.keys())
    
    for q in common_questions:
        card1 = cards1_dict[q]
        card2 = cards2_dict[q]
        
        if card1.answer != card2.answer:
            # Find the index in the original lists
            idx1 = next(i for i, card in enumerate(cards1) if card.question == q)
            differences.append((idx1, card1, card2))
    
    return differences


def identify_html_differences(text1: str, text2: str) -> List[str]:
    """Identify specific differences in HTML content."""
    # Simple character-by-character diff for demonstration
    # In a full implementation, you might use an HTML parser
    diff = difflib.ndiff(text1, text2)
    return list(diff)


def main():
    if len(sys.argv) != 3:
        print("Usage: python anki_diff.py <file1> <file2>")
        print("Example: python anki_diff.py anki-export-android.txt anki-export-macos.txt")
        sys.exit(1)
    
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    
    # Get file names for display
    file1_name = os.path.basename(file1_path)
    file2_name = os.path.basename(file2_path)
    
    print(f"\nComparing {file1_name} and {file2_name}...\n")
    
    # Load the files
    lines1 = load_anki_export(file1_path)
    lines2 = load_anki_export(file2_path)
    
    print(f"File 1 ({file1_name}): {len(lines1)} lines")
    print(f"File 2 ({file2_name}): {len(lines2)} lines\n")
    
    # Parse the exports
    headers1, cards1 = parse_anki_export(lines1)
    headers2, cards2 = parse_anki_export(lines2)
    
    print(f"File 1: {len(cards1)} cards")
    print(f"File 2: {len(cards2)} cards\n")
    
    # Compare headers
    if headers1 != headers2:
        print("Header differences:")
        for key in set(headers1.keys()) | set(headers2.keys()):
            if key not in headers1:
                print(f"  Header '{key}' only in {file2_name}: {headers2[key]}")
            elif key not in headers2:
                print(f"  Header '{key}' only in {file1_name}: {headers1[key]}")
            elif headers1[key] != headers2[key]:
                print(f"  Header '{key}' differs: {file1_name}='{headers1[key]}', {file2_name}='{headers2[key]}'")
        print()
    else:
        print("Headers are identical.\n")
    
    # Find missing cards
    missing_in_1, missing_in_2 = find_missing_cards(cards1, cards2)
    
    if missing_in_1:
        print(f"Cards in {file2_name} but missing in {file1_name}: {len(missing_in_1)}")
        for i, (q, a) in enumerate(missing_in_1[:5]):
            print(f"  {i+1}. Q: {q[:50]}... A: {a[:50]}...")
        if len(missing_in_1) > 5:
            print(f"  ... and {len(missing_in_1) - 5} more")
        print()
    
    if missing_in_2:
        print(f"Cards in {file1_name} but missing in {file2_name}: {len(missing_in_2)}")
        for i, (q, a) in enumerate(missing_in_2[:5]):
            print(f"  {i+1}. Q: {q[:50]}... A: {a[:50]}...")
        if len(missing_in_2) > 5:
            print(f"  ... and {len(missing_in_2) - 5} more")
        print()
    
    # Find content differences in shared cards
    content_differences = find_content_differences(cards1, cards2)
    
    if content_differences:
        print(f"Content differences in shared cards: {len(content_differences)}")
        for i, ((q1, a1), (q2, a2)) in enumerate([(cards1[idx], cards2[idx]) for idx, _, _ in content_differences[:5]]):
            print(f"\n  Difference {i+1}:")
            print(f"    Question: {q1[:50]}...")
            print(f"    {file1_name} Answer: {a1[:50]}...")
            print(f"    {file2_name} Answer: {a2[:50]}...")
            
            # Show a more detailed diff for this example
            if i == 0:
                print("\n    Detailed diff of first difference:")
                diff = difflib.unified_diff(a1.splitlines(), a2.splitlines(), lineterm='')
                for j, line in enumerate(diff):
                    if j > 10:  # Limit diff output
                        print("      ...")
                        break
                    print(f"      {line}")
                
        if len(content_differences) > 5:
            print(f"\n  ... and {len(content_differences) - 5} more differences")
    else:
        print("No content differences found in shared cards.")
    
    # Summary
    print("\nSummary:")
    print(f"  Total cards in {file1_name}: {len(cards1)}")
    print(f"  Total cards in {file2_name}: {len(cards2)}")
    print(f"  Cards only in {file1_name}: {len(missing_in_2)}")
    print(f"  Cards only in {file2_name}: {len(missing_in_1)}")
    print(f"  Shared cards with differences: {len(content_differences)}")
    
    difference_count = len(missing_in_1) + len(missing_in_2) + len(content_differences)
    if difference_count == 0:
        print("\nConclusion: The files are identical in content.")
    else:
        print(f"\nConclusion: Found {difference_count} total differences between the files.")
        
    # Generate a detailed report
    report_path = "anki_diff_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Anki Export Comparison Report\n")
        f.write(f"===========================\n\n")
        f.write(f"File 1: {file1_path}\n")
        f.write(f"File 2: {file2_path}\n\n")
        
        f.write(f"Summary:\n")
        f.write(f"  Total cards in File 1: {len(cards1)}\n")
        f.write(f"  Total cards in File 2: {len(cards2)}\n")
        f.write(f"  Cards only in File 1: {len(missing_in_2)}\n")
        f.write(f"  Cards only in File 2: {len(missing_in_1)}\n")
        f.write(f"  Shared cards with differences: {len(content_differences)}\n\n")
        
        if missing_in_1:
            f.write(f"Cards in File 2 but missing in File 1:\n")
            for i, (q, a) in enumerate(missing_in_1):
                f.write(f"  {i+1}. Q: {q}\n     A: {a}\n\n")
        
        if missing_in_2:
            f.write(f"Cards in File 1 but missing in File 2:\n")
            for i, (q, a) in enumerate(missing_in_2):
                f.write(f"  {i+1}. Q: {q}\n     A: {a}\n\n")
        
        if content_differences:
            f.write(f"Content differences in shared cards:\n")
            for i, (idx, (q1, a1), (q2, a2)) in enumerate(content_differences):
                f.write(f"  Difference {i+1} (card index {idx}):\n")
                f.write(f"    Question: {q1}\n")
                f.write(f"    File 1 Answer: {a1}\n")
                f.write(f"    File 2 Answer: {a2}\n\n")
    
    print(f"\nDetailed report saved to {report_path}")


if __name__ == "__main__":
    main()
