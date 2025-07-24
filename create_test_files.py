#!/usr/bin/env python3
"""
Utility script to create test ebook and comic files for testing the beets-ebooks plugin.

This script creates sample files with metadata for testing purposes:
- EPUB files with proper metadata structure
- CBZ files with ComicInfo.xml metadata
- PDF files (basic text files with PDF extension)
- MOBI files (basic text files with MOBI extension)

The created files are stored in the test_ebooks/ directory.
"""

import json
import os
import zipfile
from datetime import datetime


def ensure_test_directory():
    """Ensure the test directory exists."""
    test_dir = "test_ebooks"
    os.makedirs(test_dir, exist_ok=True)
    return test_dir


def create_epub_file(filename, metadata):
    """Create a test EPUB file with proper structure and metadata."""
    test_dir = ensure_test_directory()
    epub_path = os.path.join(test_dir, filename)

    # Create a basic EPUB structure
    with zipfile.ZipFile(epub_path, "w") as epub:
        # Add mimetype (must be first and uncompressed)
        epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

        # Add META-INF/container.xml
        container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
        epub.writestr("META-INF/container.xml", container_xml.encode("utf-8"))

        # Add content.opf with metadata
        content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">{metadata.get('identifier', 'test-book-001')}</dc:identifier>
    <dc:title>{metadata['title']}</dc:title>
    <dc:creator>{metadata['author']}</dc:creator>
    <dc:language>{metadata.get('language', 'en')}</dc:language>
    <dc:publisher>{metadata.get('publisher', 'Test Publisher')}</dc:publisher>
    <dc:date>{metadata.get('date', '2024-01-01')}</dc:date>
    <dc:description>
        {metadata.get(
            'description',
            'A test ebook for beets-ebooks plugin testing.'
        )}
    </dc:description>
  </metadata>
  <manifest>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="toc" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="toc">
    <itemref idref="chapter1"/>
  </spine>
</package>"""
        epub.writestr("OEBPS/content.opf", content_opf.encode("utf-8"))

        # Add a basic chapter
        chapter_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{metadata['title']}</title>
</head>
<body>
    <h1>{metadata['title']}</h1>
    <p>By {metadata['author']}</p>
    <p>
        {metadata.get(
            'description',
            'This is a test ebook created for testing the beets-ebooks plugin.'
        )}
    </p>
    <p>
        Metadata extracted by the plugin.
    </p>
</body>
</html>"""
        epub.writestr("OEBPS/chapter1.xhtml", chapter_content.encode("utf-8"))

        # Add basic TOC
        toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="{metadata.get('identifier', 'test-book-001')}"/>
  </head>
  <docTitle>
    <text>{metadata['title']}</text>
  </docTitle>
  <navMap>
    <navPoint id="chapter1">
      <navLabel><text>Chapter 1</text></navLabel>
      <content src="chapter1.xhtml"/>
    </navPoint>
  </navMap>
</ncx>"""
        epub.writestr("OEBPS/toc.ncx", toc_ncx.encode("utf-8"))

    print(f"Created test EPUB file: {epub_path}")
    return epub_path


def create_cbz_file(filename, comic_metadata, num_pages=3):
    """Create a test CBZ file with ComicInfo.xml metadata."""
    test_dir = ensure_test_directory()
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
    <Title>{comic_metadata['title']}</Title>
    <Series>{comic_metadata['series']}</Series>
    <Number>{comic_metadata['number']}</Number>
    <Writer>{comic_metadata['writer']}</Writer>
    <Publisher>{comic_metadata['publisher']}</Publisher>
    <Year>{comic_metadata['year']}</Year>
    <PageCount>{num_pages}</PageCount>
    <Genre>{comic_metadata['genre']}</Genre>
    <Summary>{comic_metadata['summary']}</Summary>
    <LanguageISO>{comic_metadata.get('language', 'en')}</LanguageISO>
</ComicInfo>"""
        cbz.writestr("ComicInfo.xml", comic_info_xml.encode("utf-8"))

    print(f"Created test CBZ file: {cbz_path}")
    return cbz_path


def create_simple_file(filename, content, file_type="ebook"):
    """Create a simple text-based file with basic content."""
    test_dir = ensure_test_directory()
    file_path = os.path.join(test_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Created test {file_type} file: {file_path}")
    return file_path


def create_test_ebooks():
    """Create sample ebook test files."""
    print("Creating test ebook files...")

    # Classic Literature EPUB
    tolkien_metadata = {
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "publisher": "Test Publishing",
        "date": "1954-07-29",
        "language": "en",
        "identifier": "isbn:9780000000001",
        "description": "Epic fantasy novel about the quest to destroy the One Ring.",
    }
    create_epub_file("J.R.R. Tolkien - The Lord of the Rings.epub", tolkien_metadata)

    # Mystery Novel EPUB
    christie_metadata = {
        "title": "Murder on the Orient Express",
        "author": "Agatha Christie",
        "publisher": "Mystery House",
        "date": "1934-01-01",
        "language": "en",
        "identifier": "isbn:9780000000002",
        "description": "A classic murder mystery featuring detective Hercule Poirot.",
    }
    create_epub_file("Agatha Christie - Murder on the Orient Express.epub", christie_metadata)

    # Science Fiction EPUB
    asimov_metadata = {
        "title": "Foundation",
        "author": "Isaac Asimov",
        "publisher": "Sci-Fi Books",
        "date": "1951-05-01",
        "language": "en",
        "identifier": "isbn:9780000000003",
        "description": "The first novel in Asimov's Foundation series about psychohistory.",
    }
    create_epub_file("Isaac Asimov - Foundation.epub", asimov_metadata)

    # Simple MOBI file
    mobi_content = """MOBI File Test Content
    
This is a test MOBI file for the beets-ebooks plugin.
Title: The Hitchhiker's Guide to the Galaxy
Author: Douglas Adams
Publisher: Test Books
Year: 1979

This file will be detected as a MOBI format by the plugin.
"""
    create_simple_file(
        "Douglas Adams - The Hitchhiker's Guide to the Galaxy.mobi", mobi_content, "MOBI"
    )

    # Simple PDF file
    pdf_content = """PDF File Test Content

This is a test PDF file for the beets-ebooks plugin.
Title: 1984
Author: George Orwell
Publisher: Test Publications
Year: 1949

This file will be detected as a PDF format by the plugin.
The actual PDF parsing would require additional libraries.
"""
    create_simple_file("George Orwell - 1984.pdf", pdf_content, "PDF")

    # Simple title-only book
    simple_content = """Simple Book Test Content

This is a test file with just a title for filename parsing testing.
The plugin should extract the title from the filename.
"""
    create_simple_file("Just a Title.epub", simple_content, "EPUB")


def create_test_comics():
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
    create_cbz_file("Batman - Detective Comics 001.cbz", batman_data)

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
    create_cbz_file("Spider-Man - Amazing Fantasy 015.cbr", spiderman_data)

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
    create_cbz_file("X-Men - Uncanny X-Men 001.cbz", xmen_data)


def main():
    """Create all test files."""
    print("Creating test files for beets-ebooks plugin...")
    print("=" * 50)

    create_test_ebooks()
    print()
    create_test_comics()

    print("\n" + "=" * 50)
    print("Test files created successfully!")
    print("\nYou can now test the plugin with:")
    print("  python examples/basic_usage.py")
    print("  python -m pytest tests/ -v")
    print("\nTo test with real files:")
    print(
        '  python -c "from beetsplug.ebooks import EBooksPlugin; '
        "p = EBooksPlugin(); print('EPUB detected:', "
        "p._is_ebook_file('test_ebooks/J.R.R. Tolkien - The Lord of the Rings.epub'))\""
    )

    # Show what was created
    test_dir = ensure_test_directory()
    files = os.listdir(test_dir)
    print(f"\nCreated {len(files)} test files in {test_dir}/:")
    for file in sorted(files):
        print(f"  - {file}")


if __name__ == "__main__":
    main()
