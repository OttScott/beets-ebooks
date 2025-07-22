#!/usr/bin/env python3
"""
Test script to verify CBR/CBZ support in the beets-ebooks plugin.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from beetsplug.ebooks import EBooksPlugin

def test_comic_support():
    """Test comic book support."""
    plugin = EBooksPlugin()
    
    # Test CBZ file
    cbz_path = os.path.join("test_ebooks", "Batman - Detective Comics 001.cbz")
    if os.path.exists(cbz_path):
        print(f"Testing CBZ file: {cbz_path}")
        print(f"Is ebook file: {plugin._is_ebook_file(cbz_path)}")
        
        metadata = plugin._extract_basic_metadata(cbz_path)
        print("Extracted metadata:")
        for key, value in metadata.items():
            if value:
                print(f"  {key}: {value}")
        print()
    
    # Test CBR file 
    cbr_path = os.path.join("test_ebooks", "Spider-Man - Amazing Fantasy 015.cbr")
    if os.path.exists(cbr_path):
        print(f"Testing CBR file: {cbr_path}")
        print(f"Is ebook file: {plugin._is_ebook_file(cbr_path)}")
        
        metadata = plugin._extract_basic_metadata(cbr_path)
        print("Extracted metadata:")
        for key, value in metadata.items():
            if value:
                print(f"  {key}: {value}")
        print()

    # Test file extension detection
    print("Testing file extension detection:")
    test_files = [
        "comic.cbz",
        "comic.cbr", 
        "book.epub",
        "document.pdf",
        "music.mp3"
    ]
    
    for filename in test_files:
        is_ebook = plugin._is_ebook_file(filename)
        print(f"  {filename}: {'✓' if is_ebook else '✗'}")

if __name__ == "__main__":
    test_comic_support()
