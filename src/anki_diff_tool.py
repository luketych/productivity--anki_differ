#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import webbrowser


def main():
    parser = argparse.ArgumentParser(description='Anki Export Comparison and Merge Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two Anki export files')
    compare_parser.add_argument('file1', help='First Anki export file')
    compare_parser.add_argument('file2', help='Second Anki export file')
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge two Anki export files')
    merge_parser.add_argument('file1', help='First Anki export file')
    merge_parser.add_argument('file2', help='Second Anki export file')
    merge_parser.add_argument('--output', '-o', default='merged_export.txt', 
                            help='Output file path (default: merged_export.txt)')
    merge_parser.add_argument('--conflict', '-c', default='manual', 
                            choices=['prefer_file1', 'prefer_file2', 'manual'],
                            help='Conflict resolution strategy')
    
    # View report command
    view_parser = subparsers.add_parser('view', help='View the HTML comparison report')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle the different commands
    if args.command == 'compare':
        # Run the comparison script
        cmd = [sys.executable, 'anki_diff.py', args.file1, args.file2]
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd)
        
        # Open the HTML report in a browser
        if os.path.exists('view_differences.html'):
            print("\nOpening HTML report in your browser...")
            webbrowser.open('file://' + os.path.abspath('view_differences.html'))
        
    elif args.command == 'merge':
        # Run the merge script
        cmd = [sys.executable, 'merge_exports.py', args.file1, args.file2, 
              '--output', args.output, '--conflict', args.conflict]
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd)
        
    elif args.command == 'view':
        # Open the HTML report in a browser
        if os.path.exists('view_differences.html'):
            print("Opening HTML report in your browser...")
            webbrowser.open('file://' + os.path.abspath('view_differences.html'))
        else:
            print("HTML report not found. Run 'compare' command first.")
    
    else:
        # If no command specified, show help
        parser.print_help()


if __name__ == "__main__":
    main()
