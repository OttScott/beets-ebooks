#!/usr/bin/env python3
"""
Example script demonstrating basic plugin functionality.

This script shows how the beets-ebooks plugin works without requiring
a full beets installation. It's useful for testing and development.

For production usage, the ebook-manager utility provides a more complete
CLI interface: https://github.com/OttScott/ebook-manager
"""

import json
import os
import sys
from unittest.mock import MagicMock

# Add the parent directory to the path so we can import the plugin
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Mock beets modules for this example
sys.modules["beets.plugins"] = MagicMock()
sys.modules["beets"] = MagicMock()
sys.modules["beets.library"] = MagicMock()
sys.modules["beets.dbcore"] = MagicMock()
sys.modules["beets.dbcore.types"] = MagicMock()
sys.modules["beets.importer"] = MagicMock()
sys.modules["beets.ui"] = MagicMock()

from beetsplug.ebooks import EBooksPlugin  # noqa: E402


def create_test_ebook(filename):
    """Create a test ebook file for demonstration."""
    content = f"""
    Test ebook content for {filename}
    This would be an actual ebook in a real scenario.
    """

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Created test ebook: {filename}")


def main():
    """Main example function."""
    print("Beets Ebooks Plugin Example")
    print("=" * 40)

    # Initialize the plugin
    plugin = EBooksPlugin()
    print("✓ Plugin initialized successfully")

    # Create some test ebooks
    test_files = [
        "J.R.R. Tolkien - The Lord of the Rings.epub",
        "Agatha Christie - Murder on the Orient Express.pdf",
        "Just a Title.mobi",
        "not_an_ebook.txt",
    ]

    print("\nCreating test files...")
    for filename in test_files:
        create_test_ebook(filename)

    print("\nTesting ebook file detection...")
    for filename in test_files:
        is_ebook = plugin._is_ebook_file(filename)
        status = "✓ EBOOK" if is_ebook else "✗ NOT EBOOK"
        print(f"  {filename}: {status}")

    print("\nExtracting metadata from ebook files...")
    for filename in test_files:
        if plugin._is_ebook_file(filename):
            print(f"\n📖 {filename}:")
            metadata = plugin._extract_basic_metadata(filename)
            for key, value in metadata.items():
                if value:
                    print(f"    {key}: {value}")

    print("\nTesting Google Books API metadata fetching...")
    print("(Note: This requires an internet connection)")

    try:
        # Test with a well-known book
        external_metadata = plugin._fetch_google_books_metadata(
            "The Lord of the Rings", "J.R.R. Tolkien"
        )

        if external_metadata:
            print("\n🌐 External metadata found:")
            for key, value in external_metadata.items():
                print(f"    {key}: {value}")
        else:
            print("\n⚠️  No external metadata found (this is normal without API key)")

    except Exception as e:
        print(f"\n⚠️  Error fetching external metadata: {e}")

    # Clean up test files
    print("\nCleaning up test files...")
    for filename in test_files:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"  Removed: {filename}")

    print("\n✅ Example completed successfully!")
    print("\nTo use this plugin with beets:")
    print("1. Install beets: pip install beets")
    print("2. Install this plugin: pip install -e .")
    print("3. Add 'ebooks' to your beets plugins list")
    print("4. Run: beet import /path/to/ebooks/")


if __name__ == "__main__":
    main()
