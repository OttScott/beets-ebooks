import os
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import MagicMock, Mock

# Add the parent directory to the path so we can import the plugin
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Mock beets modules before importing the plugin
mock_library = MagicMock()
mock_item_class = MagicMock()
mock_item_class._fields = {}

sys.modules["beets.plugins"] = MagicMock()
sys.modules["beets"] = MagicMock()
sys.modules["beets.library"] = MagicMock()
sys.modules["beets.library"].Library = Mock(return_value=mock_library)
sys.modules["beets.library"].Item = mock_item_class
sys.modules["beets.dbcore"] = MagicMock()
sys.modules["beets.dbcore.types"] = MagicMock()
sys.modules["beets.importer"] = MagicMock()
sys.modules["beets.ui"] = MagicMock()
sys.modules["beets.ui"].Subcommand = MagicMock()

# Mock external dependencies
sys.modules["requests"] = MagicMock()
sys.modules["ebooklib"] = MagicMock()
sys.modules["ebooklib.epub"] = MagicMock()

from beetsplug.ebooks import EBooksPlugin  # noqa: E402


class TestComicSupport(unittest.TestCase):
    """Test cases for comic book (CBR/CBZ) support."""

    def setUp(self):
        """Set up test fixtures."""
        self.plugin = EBooksPlugin()

    def test_comic_file_detection(self):
        """Test that comic book files are properly detected."""
        test_cases = [
            ("comic.cbz", True),
            ("comic.cbr", True),
            ("COMIC.CBZ", True),  # Case insensitive
            ("COMIC.CBR", True),  # Case insensitive
            ("comic.zip", False),  # Should not detect regular zip
            ("comic.rar", False),  # Should not detect regular rar
        ]

        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.plugin._is_ebook_file(filename)
                self.assertEqual(result, expected)

    def test_comic_filename_parsing(self):
        """Test parsing of comic book filenames."""
        test_cases = [
            (
                "Batman - Detective Comics 001.cbz",
                {
                    "series": "Batman",
                    "book_title": "Detective Comics",
                    "issue_number": 1,
                    "book_author": "Batman #001",
                },
            ),
            (
                "Spider-Man - Amazing Spider-Man 15.cbr",
                {
                    "series": "Spider-Man",
                    "book_title": "Amazing Spider-Man",
                    "issue_number": 15,
                    "book_author": "Spider-Man #015",
                },
            ),
            (
                "X-Men - Uncanny X-Men 001.cbz",
                {
                    "series": "X-Men",
                    "book_title": "Uncanny X-Men",
                    "issue_number": 1,
                    "book_author": "X-Men #001",
                },
            ),
        ]

        for filename, expected_metadata in test_cases:
            with self.subTest(filename=filename):
                metadata = self.plugin._parse_comic_filename(os.path.splitext(filename)[0])
                for key, expected_value in expected_metadata.items():
                    self.assertEqual(
                        metadata.get(key),
                        expected_value,
                        f"Failed for {key} in {filename}",
                    )

    def test_cbz_metadata_extraction_with_comicinfo(self):
        """Test CBZ metadata extraction with ComicInfo.xml."""
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
    <Summary>The origin story of Spider-Man.</Summary>
    <LanguageISO>en</LanguageISO>
</ComicInfo>"""
                cbz.writestr("ComicInfo.xml", comic_info.encode("utf-8"))

            # Extract metadata
            metadata = self.plugin._extract_basic_metadata(temp_path)

            # Verify expected metadata was extracted
            expected_fields = {
                "file_format": "CBZ",
                "page_count": 3,
                "published_year": 1963,
                "publisher": "Marvel Comics",
                "language": "en",
                "genre": "Superhero",
                "book_title": "Amazing Spider-Man",
                "book_author": "Stan Lee",
                "series": "Spider-Man",
                "issue_number": 1,
                "summary": "The origin story of Spider-Man.",
            }

            for field, expected_value in expected_fields.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        metadata.get(field),
                        expected_value,
                        f"Field {field} should be {expected_value}, got {metadata.get(field)}",
                    )

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_cbz_metadata_extraction_without_comicinfo(self):
        """Test CBZ metadata extraction without ComicInfo.xml (filename parsing only)."""
        with tempfile.NamedTemporaryFile(
            suffix=".cbz", delete=False, prefix="Batman - Detective Comics 001"
        ) as temp_cbz:
            temp_path = temp_cbz.name

        try:
            # Create a CBZ without ComicInfo.xml
            with zipfile.ZipFile(temp_path, "w") as cbz:
                # Add some dummy image files
                cbz.writestr("page01.jpg", b"fake image data")
                cbz.writestr("page02.jpg", b"fake image data")

            # Extract metadata
            metadata = self.plugin._extract_basic_metadata(temp_path)

            # Should have basic file format and page count
            self.assertEqual(metadata.get("file_format"), "CBZ")
            self.assertEqual(metadata.get("page_count"), 2)

            # Should extract some info from filename if it follows comic naming conventions
            # Note: The actual filename will be a temp name, so we can't test filename parsing here
            # This test mainly verifies the CBZ processing works without ComicInfo.xml

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_comic_info_xml_parsing(self):
        """Test parsing of ComicInfo.xml content."""
        comic_info_xml = """<?xml version="1.0"?>
<ComicInfo>
    <Title>Detective Comics</Title>
    <Series>Batman</Series>
    <Number>1</Number>
    <Writer>Bob Kane</Writer>
    <Publisher>DC Comics</Publisher>
    <Year>1939</Year>
    <PageCount>64</PageCount>
    <Genre>Superhero</Genre>
    <Summary>The first appearance of Batman.</Summary>
    <LanguageISO>en</LanguageISO>
</ComicInfo>"""

        metadata = self.plugin._parse_comic_info_xml(comic_info_xml.encode("utf-8"))

        expected_metadata = {
            "book_title": "Detective Comics",
            "series": "Batman",
            "issue_number": 1,
            "book_author": "Bob Kane",
            "publisher": "DC Comics",
            "published_year": 1939,
            "page_count": 64,
            "genre": "Superhero",
            "summary": "The first appearance of Batman.",
            "language": "en",
        }

        for field, expected_value in expected_metadata.items():
            with self.subTest(field=field):
                self.assertEqual(
                    metadata.get(field),
                    expected_value,
                    f"Field {field} should be {expected_value}, got {metadata.get(field)}",
                )

    def test_comic_format_detection(self):
        """Test detection of comic file formats."""
        # Test CBZ format
        cbz_metadata = self.plugin._extract_basic_metadata("test.cbz")
        self.assertEqual(cbz_metadata["file_format"], "CBZ")

        # Test CBR format
        cbr_metadata = self.plugin._extract_basic_metadata("test.cbr")
        self.assertEqual(cbr_metadata["file_format"], "CBR")

    def test_mixed_file_type_detection(self):
        """Test detection among mixed file types including comics."""
        test_files = [
            "comic.cbz",
            "comic.cbr",
            "book.epub",
            "document.pdf",
            "music.mp3",
            "image.jpg",
        ]

        ebook_files = [f for f in test_files if self.plugin._is_ebook_file(f)]
        non_ebook_files = [f for f in test_files if not self.plugin._is_ebook_file(f)]

        # Should correctly identify ebook files (including comics)
        self.assertIn("comic.cbz", ebook_files)
        self.assertIn("comic.cbr", ebook_files)
        self.assertIn("book.epub", ebook_files)
        self.assertIn("document.pdf", ebook_files)

        # Should correctly identify non-ebook files
        self.assertIn("music.mp3", non_ebook_files)
        self.assertIn("image.jpg", non_ebook_files)


if __name__ == "__main__":
    unittest.main()
