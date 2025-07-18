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
import argparse
from pathlib import Path

# Configuration - adjust these paths to match your setup
BEETS_EXE = r"F:\ottsc\AppData\Roaming\Python\Python313\Scripts\beet.exe"
EBOOK_EXTENSIONS = ['.epub', '.pdf', '.mobi', '.lrf', '.azw', '.azw3']

def is_ebook_file(filename, allowed_extensions=None):
    """Check if a file is an ebook based on its extension."""
    extensions = allowed_extensions or EBOOK_EXTENSIONS
    return any(filename.lower().endswith(ext) for ext in extensions)

def find_ebooks(directory, allowed_extensions=None):
    """Find all ebook files in a directory."""
    ebooks = []
    for root, _, files in os.walk(directory):
        for file in files:
            if is_ebook_file(file, allowed_extensions):
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

def scan_collection(directory, allowed_extensions=None):
    """Scan an ebook collection and process each file."""
    print(f"Scanning ebook collection in: {directory}")
    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    
    ebooks = find_ebooks(directory, allowed_extensions)
    
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

def import_collection(directory, allowed_extensions=None):
    """Import an ebook collection to beets library."""
    print(f"Importing ebook collection from: {directory}")
    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    
    ebooks = find_ebooks(directory, allowed_extensions)
    
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

def batch_import_ebooks(directory, allowed_extensions=None):
    """Import ebooks to beets library using batch import command."""
    print(f"Batch importing ebooks from: {directory}")
    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    
    ebooks = find_ebooks(directory, allowed_extensions)
    
    if not ebooks:
        print("No ebook files found.")
        return
    
    print(f"Found {len(ebooks)} ebook(s)")
    response = input(f"Import all {len(ebooks)} ebooks to beets library? (y/N): ")
    
    if response.lower() not in ['y', 'yes']:
        print("Import cancelled.")
        return
    
    try:
        if allowed_extensions:
            # When filtering by extensions, import files individually
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
                    if "Successfully imported" in result.stdout:
                        imported += 1
                        print("✓ Imported successfully")
                    else:
                        print("✗ Import failed")
                        
            print(f"\n✅ Batch import completed: {imported}/{len(ebooks)} ebooks imported successfully")
        else:
            # Use original directory-based import when no filtering
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

def suggest_organization(directory, allowed_extensions=None):
    """Suggest how to organize ebooks based on metadata."""
    print(f"Analyzing collection structure in: {directory}")
    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    
    ebooks = find_ebooks(directory, allowed_extensions)
    
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
    
    print("\nCollection Statistics:")
    print(f"  Total ebooks: {len(ebooks)}")
    print(f"  Unique authors: {len(authors)}")
    print(f"  File formats: {dict(formats)}")
    
    if authors:
        print("\nAuthors found:")
        for author in sorted(authors):
            print(f"  - {author}")
    
    print(f"\nSuggested organization structure:")
    print(f"  📁 {directory}/")
    print("    📁 Author Name/")
    print("      📄 Book Title.epub")
    print("    📁 Another Author/")
    print("      📄 Another Book.pdf")

def import_single_directory(directory, recursive=False, allowed_extensions=None):
    """Import ebooks from a single directory (non-recursive by default)."""
    print(f"Importing ebooks from: {directory}")
    if allowed_extensions:
        print(f"Filtering by extensions: {allowed_extensions}")
    
    if recursive:
        ebooks = find_ebooks(directory, allowed_extensions)
    else:
        # Only look in the specified directory, not subdirectories
        ebooks = []
        if os.path.isdir(directory):
            for file in os.listdir(directory):
                if is_ebook_file(file, allowed_extensions):
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

def parse_extensions(ext_arg):
    """Parse extension argument and return list of extensions."""
    if not ext_arg:
        return None
    
    # Handle comma-separated extensions
    extensions = [ext.strip() for ext in ext_arg.split(',')]
    
    # Ensure extensions start with a dot
    normalized_extensions = []
    for ext in extensions:
        if not ext.startswith('.'):
            ext = '.' + ext
        normalized_extensions.append(ext.lower())
    
    return normalized_extensions

def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Ebook Collection Manager for Beets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ebook_manager.py scan C:/Books/
  python ebook_manager.py scan C:/Books/ --ext .epub
  python ebook_manager.py import C:/Books/ --ext .epub,.pdf
  python ebook_manager.py import-dir "B:/Unsorted/Books mystery/Lee Child/Bad Luck and Trouble (95)/"
  python ebook_manager.py batch-import C:/Books/ --ext .epub
  python ebook_manager.py test-organize
        """
    )
    
    parser.add_argument('command', choices=[
        'scan', 'analyze', 'process', 'import', 'import-dir', 
        'batch-import', 'test-organize', 'organize'
    ], help='Command to execute')
    
    parser.add_argument('path', nargs='?', help='Path to directory or file')
    
    parser.add_argument('--ext', '--extensions', 
                        help='Comma-separated list of file extensions to process (e.g., .epub,.pdf)')
    
    # Handle legacy mode (if no arguments provided, show help)
    if len(sys.argv) == 1:
        print("Ebook Collection Manager for Beets")
        print("\nUsage:")
        print("  python ebook_manager.py scan <directory> [--ext .epub,.pdf]")
        print("  python ebook_manager.py analyze <directory> [--ext .epub]")
        print("  python ebook_manager.py process <file>")
        print("  python ebook_manager.py import <directory> [--ext .epub]")
        print("  python ebook_manager.py import-dir <directory> [--ext .epub]")
        print("  python ebook_manager.py batch-import <directory> [--ext .epub]")
        print("  python ebook_manager.py test-organize")
        print("  python ebook_manager.py organize")
        print("\nOptions:")
        print("  --ext EXTENSIONS    Filter by file extensions (e.g., --ext .epub,.pdf)")
        print("\nExamples:")
        print("  python ebook_manager.py scan C:/Books/")
        print("  python ebook_manager.py scan C:/Books/ --ext .epub")
        print("  python ebook_manager.py import C:/Books/ --ext .epub,.pdf")
        print("  python ebook_manager.py import-dir 'B:/Unsorted/Books mystery/Lee Child/Bad Luck and Trouble (95)/'")
        return
    
    try:
        args = parser.parse_args()
    except SystemExit:
        return
    
    # Parse extensions
    allowed_extensions = parse_extensions(args.ext)
    
    # Execute commands
    if args.command == 'scan':
        if not args.path:
            print("Error: scan command requires a directory path")
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        scan_collection(args.path, allowed_extensions)
    
    elif args.command == 'analyze':
        if not args.path:
            print("Error: analyze command requires a directory path")
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        suggest_organization(args.path, allowed_extensions)
    
    elif args.command == 'process':
        if not args.path:
            print("Error: process command requires a file path")
            return
        if not os.path.isfile(args.path):
            print(f"File not found: {args.path}")
            return
        if not is_ebook_file(args.path, allowed_extensions):
            print(f"Not an ebook file: {args.path}")
            return
        output = process_ebook_with_beets(args.path)
        if output:
            print(output)
    
    elif args.command == 'import':
        if not args.path:
            print("Error: import command requires a directory path")
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        import_collection(args.path, allowed_extensions)
    
    elif args.command == 'import-dir':
        if not args.path:
            print("Error: import-dir command requires a directory path")
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        import_single_directory(args.path, recursive=False, allowed_extensions=allowed_extensions)
    
    elif args.command == 'batch-import':
        if not args.path:
            print("Error: batch-import command requires a directory path")
            return
        if not os.path.isdir(args.path):
            print(f"Directory not found: {args.path}")
            return
        batch_import_ebooks(args.path, allowed_extensions)
    
    elif args.command == 'test-organize':
        test_organization(dry_run=True)
    
    elif args.command == 'organize':
        test_organization(dry_run=False)

if __name__ == "__main__":
    main()
