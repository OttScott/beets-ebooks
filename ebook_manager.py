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

def import_ebook_to_beets(ebook_path):
    """Import a single ebook using the beets import-ebooks command."""
    try:
        # Use absolute path to avoid path issues
        abs_path = os.path.abspath(ebook_path)
        result = subprocess.run(
            [BEETS_EXE, 'import-ebooks', abs_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error importing {ebook_path}: {e}")
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

def import_collection(directory):
    """Import an ebook collection to beets library."""
    print(f"Importing ebook collection from: {directory}")
    ebooks = find_ebooks(directory)
    
    if not ebooks:
        print("No ebook files found.")
        return
    
    print(f"Found {len(ebooks)} ebook(s)")
    response = input(f"Import all {len(ebooks)} ebooks to beets library? (y/N): ")
    
    if response.lower() not in ['y', 'yes']:
        print("Import cancelled.")
        return
    
    print("-" * 50)
    imported = 0
    
    for i, ebook in enumerate(ebooks, 1):
        print(f"\n[{i}/{len(ebooks)}] Importing: {os.path.basename(ebook)}")
        output = import_ebook_to_beets(ebook)
        if output and "Successfully imported" in output:
            imported += 1
            print("✓ Imported successfully")
        else:
            print("✗ Import failed")
        
    print("-" * 50)
    print(f"Import completed: {imported}/{len(ebooks)} ebooks imported successfully")

def batch_import_ebooks(directory):
    """Import ebooks to beets library using batch import command."""
    print(f"Batch importing ebooks from: {directory}")
    ebooks = find_ebooks(directory)
    
    if not ebooks:
        print("No ebook files found.")
        return
    
    print(f"Found {len(ebooks)} ebook(s)")
    response = input(f"Import all {len(ebooks)} ebooks to beets library? (y/N): ")
    
    if response.lower() not in ['y', 'yes']:
        print("Import cancelled.")
        return
    
    try:
        # Use absolute path to avoid path issues
        abs_directory = os.path.abspath(directory)
        result = subprocess.run(
            [BEETS_EXE, 'import-ebooks', abs_directory],
            capture_output=True,
            text=True,
            check=True
        )
        print("Batch import completed successfully!")
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error importing ebooks: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
    except FileNotFoundError:
        print(f"Beets executable not found at {BEETS_EXE}")

def test_organization(dry_run=True):
    """Test ebook organization in beets."""
    print("Testing ebook organization...")
    
    # First, show current ebooks in library
    try:
        result = subprocess.run(
            [BEETS_EXE, 'ls', 'ebook:true'],
            capture_output=True,
            text=True,
            check=True
        )
        if not result.stdout.strip():
            print("No ebooks found in beets library.")
            return
        
        print("Current ebooks in library:")
        print(result.stdout)
        
        # Show what the move operation would do
        cmd = [BEETS_EXE, 'move', 'ebook:true']
        if dry_run:
            cmd.append('--pretend')
            print("\nDry run - showing what would happen:")
        else:
            print("\nActually moving files:")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        
        if not dry_run:
            print("Files have been organized!")
            # Show new paths
            result = subprocess.run(
                [BEETS_EXE, 'ls', '-f', '$path', 'ebook:true'],
                capture_output=True,
                text=True,
                check=True
            )
            print("\nNew file locations:")
            print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Error testing organization: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
    except FileNotFoundError:
        print(f"Beets executable not found at {BEETS_EXE}")

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

def import_single_directory(directory, recursive=False):
    """Import ebooks from a single directory (non-recursive by default)."""
    print(f"Importing ebooks from: {directory}")
    
    if recursive:
        ebooks = find_ebooks(directory)
    else:
        # Only look in the specified directory, not subdirectories
        ebooks = []
        if os.path.isdir(directory):
            for file in os.listdir(directory):
                if is_ebook_file(file):
                    ebooks.append(os.path.join(directory, file))
    
    if not ebooks:
        print("No ebook files found.")
        return
    
    print(f"Found {len(ebooks)} ebook(s):")
    for i, ebook in enumerate(ebooks, 1):
        print(f"  {i}. {os.path.basename(ebook)}")
    
    response = input(f"\nImport all {len(ebooks)} ebooks to beets library? (y/N): ")
    
    if response.lower() not in ['y', 'yes']:
        print("Import cancelled.")
        return
    
    try:
        imported = 0
        for ebook in ebooks:
            print(f"\nImporting: {os.path.basename(ebook)}")
            abs_path = os.path.abspath(ebook)
            result = subprocess.run(
                [BEETS_EXE, 'import-ebooks', abs_path],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                print(result.stdout.strip())
                if "Successfully imported" in result.stdout:
                    imported += 1
        
        print(f"\n✅ Import completed: {imported}/{len(ebooks)} ebooks imported successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"Error importing ebooks: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
    except FileNotFoundError:
        print(f"Beets executable not found at {BEETS_EXE}")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Ebook Collection Manager for Beets")
        print("\nUsage:")
        print("  python ebook_manager.py scan <directory>         - Scan and process all ebooks")
        print("  python ebook_manager.py analyze <directory>      - Analyze collection structure")
        print("  python ebook_manager.py process <file>           - Process single ebook")
        print("  python ebook_manager.py import <directory>       - Import collection to beets")
        print("  python ebook_manager.py import-dir <directory>   - Import single directory (non-recursive)")
        print("  python ebook_manager.py batch-import <directory> - Batch import collection to beets")
        print("  python ebook_manager.py test-organize            - Test organization (dry run)")
        print("  python ebook_manager.py organize                 - Actually organize files")
        print("\nExamples:")
        print("  python ebook_manager.py scan C:/Books/")
        print("  python ebook_manager.py import C:/Books/")
        print("  python ebook_manager.py import-dir 'B:/Unsorted/Books mystery/Lee Child/Bad Luck and Trouble (95)/'")
        print("  python ebook_manager.py test-organize")
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
    
    elif command == 'import' and len(sys.argv) >= 3:
        directory = sys.argv[2]
        if os.path.isdir(directory):
            import_collection(directory)
        else:
            print(f"Directory not found: {directory}")
    
    elif command == 'import-dir' and len(sys.argv) >= 3:
        directory = sys.argv[2]
        if os.path.isdir(directory):
            import_single_directory(directory)
        else:
            print(f"Directory not found: {directory}")
    
    elif command == 'batch-import' and len(sys.argv) >= 3:
        directory = sys.argv[2]
        if os.path.isdir(directory):
            batch_import_ebooks(directory)
        else:
            print(f"Directory not found: {directory}")
    
    elif command == 'test-organize':
        test_organization(dry_run=True)
    
    elif command == 'organize':
        test_organization(dry_run=False)
    
    else:
        print("Invalid command or missing arguments.")
        print("Use 'python ebook_manager.py' for usage information.")

if __name__ == "__main__":
    main()
