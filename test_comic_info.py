#!/usr/bin/env python3
"""
Test script to verify CBZ ComicInfo.xml metadata extraction.
"""

import os
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(__file__))

from beetsplug.ebooks import EBooksPlugin  # noqa: E402


def test_comic_info_xml_extraction():
    """Test extraction of metadata from ComicInfo.xml in CBZ files."""
    plugin = EBooksPlugin()

    # Create a temporary CBZ file with ComicInfo.xml
    with tempfile.NamedTemporaryFile(suffix=".cbz", delete=False) as temp_cbz:
        temp_path = temp_cbz.name

    try:
        # Create a CBZ with ComicInfo.xml
        with zipfile.ZipFile(temp_path, "w") as cbz:
            # Add some dummy image files
            cbz.writestr("page01.jpg", b"fake image data")
            cbz.writestr("page02.jpg", b"fake image data")
            cbz.writestr("page03.jpg", b"fake image data")

            # Add ComicInfo.xml with comprehensive metadata
            comic_info = """<?xml version="1.0"?>
<ComicInfo>
    <Title>Amazing Spider-Man</Title>
    <Series>Spider-Man</Series>
    <Number>1</Number>
    <Writer>Stan Lee</Writer>
    <Publisher>Marvel Comics</Publisher>
    <Year>1963</Year>
    <PageCount>3</PageCount>
    <Genre>Superhero</Genre>
    <Summary>The origin story of Spider-Man, featuring Peter Parker's transformation """ \
        """into the amazing wall-crawler.</Summary>
    <LanguageISO>en</LanguageISO>
</ComicInfo>"""
            cbz.writestr("ComicInfo.xml", comic_info.encode("utf-8"))

        print(f"Testing CBZ with ComicInfo.xml: {temp_path}")

        # Extract metadata
        metadata = plugin._extract_basic_metadata(temp_path)

        print("Extracted metadata:")
        for key, value in metadata.items():
            if value:
                print(f"  {key}: {value}")

        # Verify expected metadata was extracted
        expected_fields = {
            "file_format": "CBZ",
            "page_count": 3,
            "published_year": 1963,
            "publisher": "Marvel Comics",
            "language": "en",
            "genre": "Superhero",
        }

        print("\nVerification:")
        all_passed = True
        for field, expected_value in expected_fields.items():
            actual_value = metadata.get(field)
            if actual_value == expected_value:
                print(f"  ✓ {field}: {actual_value}")
            else:
                print(f"  ✗ {field}: expected {expected_value}, got {actual_value}")
                all_passed = False

        if all_passed:
            print("\n🎉 All ComicInfo.xml metadata fields extracted successfully!")
        else:
            print("\n❌ Some metadata fields were not extracted correctly.")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


if __name__ == "__main__":
    test_comic_info_xml_extraction()
