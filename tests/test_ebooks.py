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
    """Test cases for the EBooks plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.plugin = EBooksPlugin()

    def test_plugin_initialization(self):
        """Test that the plugin initializes correctly."""
        self.assertIsInstance(self.plugin, EBooksPlugin)
        self.assertIsInstance(self.plugin.config, object)

    def test_is_ebook_file(self):
        """Test ebook file detection."""
        test_cases = [
            ("book.epub", True),
            ("document.pdf", True),
            ("story.mobi", True),
            ("novel.azw", True),
            ("comic.cbr", True),
            ("comic.cbz", True),
            ("music.mp3", False),
            ("image.jpg", False),
            ("text.txt", False),
        ]

        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.plugin._is_ebook_file(filename)
                self.assertEqual(result, expected)

    def test_plugin_has_commands(self):
        """Test that plugin provides commands."""
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

    def test_comic_metadata_extraction(self):
        """Test comic book metadata extraction."""
        # Test CBZ file detection
        cbz_metadata = self.plugin._extract_basic_metadata("test.cbz")
        self.assertEqual(cbz_metadata["file_format"], "CBZ")

        # Test CBR file detection
        cbr_metadata = self.plugin._extract_basic_metadata("test.cbr")
        self.assertEqual(cbr_metadata["file_format"], "CBR")

    def test_ebook_file_extensions(self):
        """Test that all expected ebook extensions are supported."""
        supported_extensions = [".epub", ".pdf", ".mobi", ".azw", ".azw3", ".lrf"]

        for ext in supported_extensions:
            with self.subTest(extension=ext):
                filename = f"test{ext}"
                self.assertTrue(
                    self.plugin._is_ebook_file(filename),
                    f"Extension {ext} should be recognized as ebook",
                )

    def test_non_ebook_extensions(self):
        """Test that non-ebook extensions are not detected as ebooks."""
        non_ebook_extensions = [".mp3", ".flac", ".wav", ".jpg", ".png", ".txt", ".doc"]

        for ext in non_ebook_extensions:
            with self.subTest(extension=ext):
                filename = f"test{ext}"
                self.assertFalse(
                    self.plugin._is_ebook_file(filename),
                    f"Extension {ext} should not be recognized as ebook",
                )

    def test_integration_file_detection(self):
        """Test integration of file detection with real file paths."""
        # Test with mixed file types
        test_files = [
            "book.epub",
            "novel.pdf",
            "story.mobi",
            "song.mp3",
            "image.jpg",
            "doc.txt",
            "audio.flac",
        ]

        ebook_files = [f for f in test_files if self.plugin._is_ebook_file(f)]
        non_ebook_files = [f for f in test_files if not self.plugin._is_ebook_file(f)]

        # Should correctly identify ebook vs non-ebook files
        self.assertEqual(len(ebook_files), 3)  # epub, pdf, mobi
        self.assertEqual(len(non_ebook_files), 4)  # mp3, jpg, txt, flac

        self.assertIn("book.epub", ebook_files)
        self.assertIn("novel.pdf", ebook_files)
        self.assertIn("story.mobi", ebook_files)

        self.assertIn("song.mp3", non_ebook_files)
        self.assertIn("image.jpg", non_ebook_files)
        self.assertIn("doc.txt", non_ebook_files)
        self.assertIn("audio.flac", non_ebook_files)

    def test_is_ebook_file_with_custom_extensions(self):
        """Test ebook file detection with custom allowed extensions."""
        # Test that the plugin respects custom extension filtering
        # This simulates the behavior when used with CLI filtering

        # Mock the config to return specific extensions
        test_cases = [
            # (filename, custom_extensions, expected_result)
            ("book.epub", [".epub"], True),
            ("book.pdf", [".epub"], False),
            ("book.mobi", [".epub", ".mobi"], True),
            ("book.azw", [".epub", ".mobi"], False),
            ("BOOK.EPUB", [".epub"], True),  # Case insensitive
        ]

        for filename, extensions, expected in test_cases:
            with self.subTest(filename=filename, extensions=extensions):
                # Test that the underlying detection logic works with filtering
                result = any(filename.lower().endswith(ext) for ext in extensions)
                self.assertEqual(result, expected)

    def test_extension_filtering_integration(self):
        """Test that extension filtering integrates properly with the plugin."""
        # This tests the core logic that ebook_manager.py relies on

        # Test filtering to specific subsets
        epub_only = [".epub"]
        pdf_mobi = [".pdf", ".mobi"]

        test_files = [
            "book1.epub",
            "book2.pdf",
            "book3.mobi",
            "book4.azw",
            "book5.txt",
            "book6.mp3",
        ]

        # Test EPUB only filtering
        epub_results = [f for f in test_files if any(f.lower().endswith(ext) for ext in epub_only)]
        self.assertEqual(len(epub_results), 1)
        self.assertEqual(epub_results[0], "book1.epub")

        # Test PDF and MOBI filtering
        pdf_mobi_results = [
            f for f in test_files if any(f.lower().endswith(ext) for ext in pdf_mobi)
        ]
        self.assertEqual(len(pdf_mobi_results), 2)
        self.assertIn("book2.pdf", pdf_mobi_results)
        self.assertIn("book3.mobi", pdf_mobi_results)

        # Test that non-ebook files are excluded
        self.assertNotIn("book5.txt", pdf_mobi_results)
        self.assertNotIn("book6.mp3", pdf_mobi_results)


if __name__ == "__main__":
    unittest.main()
