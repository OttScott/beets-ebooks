#!/usr/bin/env python3
"""
Demonstration of the --onefile feature in ebook_manager.py

This script demonstrates how the --onefile feature works by:
1. Showing all ebooks in the test directory
2. Showing what gets selected with --onefile
3. Demonstrating combination with --ext filtering
"""

import subprocess

# Path to the ebook_manager script
PYTHON_EXE = r"E:/Program Files/Python313/python.exe"
EBOOK_MANAGER = "ebook_manager.py"
TEST_DIR = "test_ebooks"

def run_command(command_args):
    """Run a command and capture output."""
    try:
        result = subprocess.run(
            [PYTHON_EXE] + command_args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e}\n{e.stdout}\n{e.stderr}"

def main():
    """Demonstrate the --onefile feature."""
    print("=" * 70)
    print("DEMONSTRATION: --onefile Feature in Beets Ebooks Manager")
    print("=" * 70)
    
    print("\n1. First, let's see ALL ebooks in the test directory:")
    print("-" * 50)
    output = run_command([EBOOK_MANAGER, "analyze", TEST_DIR])
    print(output)
    
    print("\n2. Now with --onefile (selects highest priority format per book):")
    print("-" * 50)
    output = run_command([EBOOK_MANAGER, "analyze", TEST_DIR, "--onefile"])
    print(output)
    
    print("\n3. Combining --onefile with --ext (filter first, then select best):")
    print("-" * 50)
    output = run_command([EBOOK_MANAGER, "analyze", TEST_DIR, "--ext", ".mobi,.epub", "--onefile"])
    print(output)
    
    print("\n4. Priority order (highest to lowest):")
    print("-" * 50)
    priority_order = [
        (".epub", "6 - Highest priority (widely supported, good for all devices)"),
        (".mobi", "5 - Amazon Kindle format"),
        (".azw", "4 - Amazon Kindle format"),
        (".azw3", "3 - Amazon Kindle format"),
        (".pdf", "2 - Portable Document Format"),
        (".lrf", "1 - Lowest priority (Sony format)")
    ]
    
    for ext, description in priority_order:
        print(f"  {ext:6} - {description}")
    
    print("\n5. How it works:")
    print("-" * 50)
    print("  • Groups books by 'Author - Title' pattern")
    print("  • For each group, selects the format with highest priority")
    print("  • Skips duplicate formats of the same book")
    print("  • Perfect for importing clean collections without duplicates")
    
    print("\n6. Usage examples:")
    print("-" * 50)
    print("  # Import only the best format per book")
    print(f"  python {EBOOK_MANAGER} import /path/to/books --onefile")
    print()
    print("  # Import only epub/mobi, with best format per book")
    print(f"  python {EBOOK_MANAGER} import /path/to/books --ext .epub,.mobi --onefile")
    print()
    print("  # Scan and analyze what would be imported")
    print(f"  python {EBOOK_MANAGER} scan /path/to/books --onefile")
    
    print("\n" + "=" * 70)
    print("End of demonstration")
    print("=" * 70)

if __name__ == "__main__":
    main()
