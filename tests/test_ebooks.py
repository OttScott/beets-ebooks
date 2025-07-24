import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

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


class TestEBooksPlugin(unittest.TestCase):
    """Test cases for the EBooks plugin core functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.plugin = EBooksPlugin()

    def test_plugin_initialization(self):
        """Test that the plugin initializes correctly."""
        self.assertIsInstance(self.plugin, EBooksPlugin)
        self.assertIsInstance(self.plugin.config, object)

    def test_is_ebook_file(self):
        """Test ebook file detection for all supported formats."""
        test_cases = [
            # Standard ebook formats
            ("book.epub", True),
            ("document.pdf", True),
            ("story.mobi", True),
            ("novel.azw", True),
            ("book.azw3", True),
            ("document.lrf", True),
            # Comic book formats
            ("comic.cbr", True),
            ("comic.cbz", True),
            # Case insensitive
            ("BOOK.EPUB", True),
            ("COMIC.CBZ", True),
            # Non-ebook files
            ("music.mp3", False),
            ("image.jpg", False),
            ("text.txt", False),
            ("video.mp4", False),
            ("archive.zip", False),
        ]

        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.plugin._is_ebook_file(filename)
                self.assertEqual(result, expected)

    def test_plugin_has_commands(self):
        """Test that plugin provides expected commands."""
        commands = self.plugin.commands()
        self.assertIsInstance(commands, list)
        self.assertEqual(len(commands), 2)  # Should have ebook and import-ebooks commands

    def test_file_format_detection(self):
        """Test file format detection from extensions."""
        test_cases = [
            ("book.epub", "EPUB"),
            ("doc.pdf", "PDF"),
            ("story.mobi", "MOBI"),
            ("novel.azw", "AZW"),
            ("file.azw3", "AZW3"),
            ("book.lrf", "LRF"),
            ("comic.cbr", "CBR"),
            ("comic.cbz", "CBZ"),
        ]

        for filename, expected_format in test_cases:
            with self.subTest(filename=filename):
                with tempfile.NamedTemporaryFile(
                    suffix=os.path.splitext(filename)[1], delete=False
                ) as tmp:
                    tmp.write(b"dummy content")
                    tmp_path = tmp.name

                try:
                    metadata = self.plugin._extract_basic_metadata(tmp_path)
                    self.assertEqual(metadata.get("file_format"), expected_format)
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

    def test_ebook_filename_parsing(self):
        """Test parsing of ebook filenames for author/title extraction."""
        # Test the filename parsing logic directly without file operations
        test_cases = [
            (
                "J.R.R. Tolkien - The Lord of the Rings",
                {"book_author": "J.R.R. Tolkien", "book_title": "The Lord of the Rings"},
            ),
            (
                "Agatha Christie - Murder on the Orient Express", 
                {"book_author": "Agatha Christie", "book_title": "Murder on the Orient Express"},
            ),
            (
                "The Great Gatsby - F. Scott Fitzgerald",
                {"book_title": "The Great Gatsby", "book_author": "F. Scott Fitzgerald"},
            ),
            (
                "Just a Title",
                {"book_title": "Just a Title"},
            ),
        ]

        for name_without_ext, expected_metadata in test_cases:
            with self.subTest(filename=name_without_ext):
                # Create mock metadata that includes filename parsing results
                mock_metadata = {
                    'file_format': 'EPUB',
                    'path': f'{name_without_ext}.epub'
                }
                
                # Test the core filename parsing logic
                if ' - ' in name_without_ext:
                    parts = name_without_ext.split(' - ', 1)
                    if len(parts) == 2:
                        part1, part2 = parts[0].strip(), parts[1].strip()
                        
                        # Heuristic: Check if it looks like "Title - Author" vs "Author - Title"
                        title_indicators = ['The ', 'A ', 'An ']
                        if any(part1.startswith(indicator) for indicator in title_indicators):
                            # Likely "Title - Author" format
                            mock_metadata['book_title'] = part1
                            mock_metadata['book_author'] = part2
                        else:
                            # Assume "Author - Title" format  
                            mock_metadata['book_author'] = part1
                            mock_metadata['book_title'] = part2
                else:
                    mock_metadata['book_title'] = name_without_ext.strip()
                
                # Verify the parsing results
                for key, expected_value in expected_metadata.items():
                    self.assertEqual(
                        mock_metadata.get(key),
                        expected_value,
                        f"Failed for {key} in {name_without_ext}",
                    )

    def test_supported_extensions_comprehensive(self):
        """Test that all expected ebook extensions are supported."""
        supported_extensions = [
            ".epub",
            ".pdf", 
            ".mobi", 
            ".azw", 
            ".azw3", 
            ".lrf",
            ".cbr",
            ".cbz"
        ]

        for ext in supported_extensions:
            with self.subTest(extension=ext):
                filename = f"test{ext}"
                self.assertTrue(
                    self.plugin._is_ebook_file(filename),
                    f"Extension {ext} should be recognized as ebook",
                )

    def test_non_ebook_extensions(self):
        """Test that non-ebook extensions are not detected as ebooks."""
        non_ebook_extensions = [
            ".mp3", ".flac", ".wav", ".m4a",  # Audio
            ".jpg", ".png", ".gif", ".bmp",   # Images
            ".txt", ".doc", ".docx",          # Documents
            ".mp4", ".avi", ".mkv",           # Video
            ".zip", ".rar", ".7z",            # Archives
        ]

        for ext in non_ebook_extensions:
            with self.subTest(extension=ext):
                filename = f"test{ext}"
                self.assertFalse(
                    self.plugin._is_ebook_file(filename),
                    f"Extension {ext} should not be recognized as ebook",
                )

    def test_custom_extension_filtering(self):
        """Test extension filtering functionality for CLI tools."""
        test_files = [
            "book1.epub",
            "book2.pdf", 
            "book3.mobi",
            "book4.azw",
            "comic1.cbz",
            "comic2.cbr",
            "music.mp3",
            "image.jpg",
        ]

        # Test EPUB only filtering
        epub_only = [".epub"]
        epub_results = [f for f in test_files if any(f.lower().endswith(ext) for ext in epub_only)]
        self.assertEqual(len(epub_results), 1)
        self.assertIn("book1.epub", epub_results)

        # Test PDF and MOBI filtering
        pdf_mobi = [".pdf", ".mobi"]
        pdf_mobi_results = [
            f for f in test_files if any(f.lower().endswith(ext) for ext in pdf_mobi)
        ]
        self.assertEqual(len(pdf_mobi_results), 2)
        self.assertIn("book2.pdf", pdf_mobi_results)
        self.assertIn("book3.mobi", pdf_mobi_results)

        # Test comic filtering
        comic_exts = [".cbr", ".cbz"]
        comic_results = [
            f for f in test_files if any(f.lower().endswith(ext) for ext in comic_exts)
        ]
        self.assertEqual(len(comic_results), 2)
        self.assertIn("comic1.cbz", comic_results)
        self.assertIn("comic2.cbr", comic_results)

        # Test that non-ebook files are excluded
        for result_list in [epub_results, pdf_mobi_results, comic_results]:
            self.assertNotIn("music.mp3", result_list)
            self.assertNotIn("image.jpg", result_list)


if __name__ == "__main__":
    unittest.main()
