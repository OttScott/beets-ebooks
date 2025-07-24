#!/usr/bin/env python3
"""
Utility script to create test comic book files for testing the beets-ebooks plugin.

This script creates sample CBZ files with ComicInfo.xml metadata for testing purposes.
The created files are stored in the test_ebooks/ directory.
"""

import os
import zipfile


def create_test_cbz(filename, comic_info_data, num_pages=3):
    """Create a test CBZ file with ComicInfo.xml metadata."""
    test_dir = "test_ebooks"
    os.makedirs(test_dir, exist_ok=True)

    cbz_path = os.path.join(test_dir, filename)

    # Create a ZIP file with dummy image files and ComicInfo.xml
    with zipfile.ZipFile(cbz_path, "w") as cbz:
        # Add dummy image files
        for i in range(1, num_pages + 1):
            page_name = f"page{i:03d}.jpg"
            cbz.writestr(page_name, b"fake image data for " + page_name.encode())

        # Add ComicInfo.xml with provided metadata
        comic_info_xml = f"""<?xml version="1.0"?>
<ComicInfo>
    <Title>{comic_info_data['title']}</Title>
    <Series>{comic_info_data['series']}</Series>
    <Number>{comic_info_data['number']}</Number>
    <Writer>{comic_info_data['writer']}</Writer>
    <Publisher>{comic_info_data['publisher']}</Publisher>
    <Year>{comic_info_data['year']}</Year>
    <PageCount>{num_pages}</PageCount>
    <Genre>{comic_info_data['genre']}</Genre>
    <Summary>{comic_info_data['summary']}</Summary>
    <LanguageISO>{comic_info_data.get('language', 'en')}</LanguageISO>
</ComicInfo>"""
        cbz.writestr("ComicInfo.xml", comic_info_xml.encode("utf-8"))

    print(f"Created test CBZ file: {cbz_path}")
    return cbz_path


def main():
    """Create sample comic book test files."""
    print("Creating test comic book files...")

    # Batman - Detective Comics #1
    batman_data = {
        "title": "Detective Comics",
        "series": "Batman",
        "number": 1,
        "writer": "Bob Kane",
        "publisher": "DC Comics",
        "year": 1939,
        "genre": "Superhero",
        "summary": "The first appearance of Batman in Detective Comics.",
    }
    create_test_cbz("Batman - Detective Comics 001.cbz", batman_data)

    # Spider-Man - Amazing Fantasy #15
    spiderman_data = {
        "title": "Amazing Fantasy",
        "series": "Spider-Man",
        "number": 15,
        "writer": "Stan Lee",
        "publisher": "Marvel Comics",
        "year": 1962,
        "genre": "Superhero",
        "summary": "The origin story of Spider-Man, featuring Peter Parker.",
    }
    create_test_cbz(
        "Spider-Man - Amazing Fantasy 015.cbr", spiderman_data
    )  # Note: .cbr extension for variety

    # X-Men - Uncanny X-Men #1
    xmen_data = {
        "title": "Uncanny X-Men",
        "series": "X-Men",
        "number": 1,
        "writer": "Stan Lee",
        "publisher": "Marvel Comics",
        "year": 1963,
        "genre": "Superhero",
        "summary": "The debut of the X-Men superhero team.",
    }
    create_test_cbz("X-Men - Uncanny X-Men 001.cbz", xmen_data)

    print("\nTest files created successfully!")
    print("You can now test the plugin with:")
    print("  python examples/basic_usage.py")
    print("  python -m pytest tests/ -v")


if __name__ == "__main__":
    main()
