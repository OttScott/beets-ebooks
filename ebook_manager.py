#!/usr/bin/env python3
"""
Ebook Collection Manager for Beets

This script helps manage your ebook collection using the beets-ebooks plugin.
It can scan directories, extract metadata, and organize your ebooks.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Configuration - adjust these paths to match your setup
BEETS_EXE = r"F:\ottsc\AppData\Roaming\Python\Python313\Scripts\beet.exe"
EBOOK_EXTENSIONS = ['.epub', '.pdf', '.mobi', '.lrf', '.azw', '.azw3']

def is_ebook_file(filename):
    """Check if a file is an ebook based on its extension."""
    return any(filename.lower().endswith(ext) for ext in EBOOK_EXTENSIONS)

def find_ebooks(directory):
    """Find all ebook files in a directory."""
    ebooks = []
    for root, _, files in os.walk(directory):
        for file in files:
            if is_ebook_file(file):
                ebooks.append(os.path.join(root, file))
    return ebooks

def process_ebook_with_beets(ebook_path):
    """Process an ebook using the beets ebook command."""
    try:
        result = subprocess.run(
            [BEETS_EXE, 'ebook', ebook_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error processing {ebook_path}: {e}")
        return None
    except FileNotFoundError:
        print(f"Beets executable not found at {BEETS_EXE}")
        return None

def scan_collection(directory):
    """Scan an ebook collection and process each file."""
    print(f"Scanning ebook collection in: {directory}")
    ebooks = find_ebooks(directory)
    
    if not ebooks:
        print("No ebook files found.")
        return
    
    print(f"Found {len(ebooks)} ebook(s)")
    print("-" * 50)
    
    for i, ebook in enumerate(ebooks, 1):
        print(f"\n[{i}/{len(ebooks)}] Processing: {os.path.basename(ebook)}")
        output = process_ebook_with_beets(ebook)
        if output:
            print(output.strip())
        print("-" * 50)

def suggest_organization(directory):
    """Suggest how to organize ebooks based on metadata."""
    print(f"Analyzing collection structure in: {directory}")
    ebooks = find_ebooks(directory)
    
    if not ebooks:
        print("No ebook files found.")
        return
    
    authors = set()
    formats = {}
    
    for ebook in ebooks:
        # Extract basic info from filename
        filename = os.path.basename(ebook)
        name_without_ext = os.path.splitext(filename)[0]
        
        if ' - ' in name_without_ext:
            parts = name_without_ext.split(' - ', 1)
            if len(parts) == 2:
                author = parts[0].strip()
                authors.add(author)
        
        # Count formats
        ext = os.path.splitext(filename)[1].lower()
        formats[ext] = formats.get(ext, 0) + 1
    
    print(f"\nCollection Statistics:")
    print(f"  Total ebooks: {len(ebooks)}")
    print(f"  Unique authors: {len(authors)}")
    print(f"  File formats: {dict(formats)}")
    
    if authors:
        print(f"\nAuthors found:")
        for author in sorted(authors):
            print(f"  - {author}")
    
    print(f"\nSuggested organization structure:")
    print(f"  📁 {directory}/")
    print(f"    📁 Author Name/")
    print(f"      📄 Book Title.epub")
    print(f"    📁 Another Author/")
    print(f"      📄 Another Book.pdf")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Ebook Collection Manager for Beets")
        print("\nUsage:")
        print("  python ebook_manager.py scan <directory>     - Scan and process all ebooks")
        print("  python ebook_manager.py analyze <directory>  - Analyze collection structure")
        print("  python ebook_manager.py process <file>       - Process single ebook")
        print("\nExamples:")
        print("  python ebook_manager.py scan C:/Books/")
        print("  python ebook_manager.py process 'book.epub'")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'scan' and len(sys.argv) >= 3:
        directory = sys.argv[2]
        if os.path.isdir(directory):
            scan_collection(directory)
        else:
            print(f"Directory not found: {directory}")
    
    elif command == 'analyze' and len(sys.argv) >= 3:
        directory = sys.argv[2]
        if os.path.isdir(directory):
            suggest_organization(directory)
        else:
            print(f"Directory not found: {directory}")
    
    elif command == 'process' and len(sys.argv) >= 3:
        file_path = sys.argv[2]
        if os.path.isfile(file_path):
            if is_ebook_file(file_path):
                output = process_ebook_with_beets(file_path)
                if output:
                    print(output)
            else:
                print(f"Not an ebook file: {file_path}")
        else:
            print(f"File not found: {file_path}")
    
    else:
        print("Invalid command or missing arguments.")
        print("Use 'python ebook_manager.py' for usage information.")

if __name__ == "__main__":
    main()
