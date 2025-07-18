import unittest
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the plugin
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Mock beets modules before importing the plugin
sys.modules['beets.plugins'] = MagicMock()
sys.modules['beets'] = MagicMock()
sys.modules['beets.library'] = MagicMock()
sys.modules['beets.dbcore'] = MagicMock()
sys.modules['beets.dbcore.types'] = MagicMock()
sys.modules['beets.importer'] = MagicMock()
sys.modules['beets.ui'] = MagicMock()

# Mock external dependencies
sys.modules['requests'] = MagicMock()
sys.modules['ebooklib'] = MagicMock()
sys.modules['ebooklib.epub'] = MagicMock()

from beetsplug.ebooks import EBooksPlugin


class TestEBooksPlugin(unittest.TestCase):
    """Test cases for the EBooks plugin."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.plugin = EBooksPlugin()
    
    def test_plugin_initialization(self):
        """Test that the plugin initializes correctly."""
        self.assertIsInstance(self.plugin, EBooksPlugin)
        self.assertIn('google_api_key', self.plugin.config.keys())
        self.assertIn('download_covers', self.plugin.config.keys())
    
    def test_is_ebook_file(self):
        """Test ebook file detection."""
        test_cases = [
            ('book.epub', True),
            ('document.pdf', True),
            ('story.mobi', True),
            ('novel.azw', True),
            ('music.mp3', False),
            ('image.jpg', False),
            ('text.txt', False),
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = self.plugin._is_ebook_file(filename)
                self.assertEqual(result, expected)
    
    def test_extract_basic_metadata_from_filename(self):
        """Test basic metadata extraction from filename."""
        test_cases = [
            ('Author Name - Book Title.epub', 'Author Name', 'Book Title'),
            ('Just a Title.pdf', None, 'Just a Title'),
            ('Complex - Multi Part - Title.mobi', 'Complex', 'Multi Part - Title'),
        ]
        
        for filename, expected_author, expected_title in test_cases:
            with self.subTest(filename=filename):
                with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp:
                    tmp.write(b'dummy content')
                    tmp_path = tmp.name
                
                try:
                    # Rename to match test filename
                    test_path = os.path.join(os.path.dirname(tmp_path), filename)
                    os.rename(tmp_path, test_path)
                    
                    metadata = self.plugin._extract_basic_metadata(test_path)
                    
                    if expected_author:
                        self.assertEqual(metadata.get('book_author'), expected_author)
                    self.assertEqual(metadata.get('book_title'), expected_title)
                    self.assertIn('file_format', metadata)
                finally:
                    # Clean up
                    if os.path.exists(test_path):
                        os.unlink(test_path)
                    elif os.path.exists(tmp_path):
                        os.unlink(tmp_path)
    
    @patch('requests.get')
    def test_fetch_google_books_metadata(self, mock_get):
        """Test Google Books API metadata fetching."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'totalItems': 1,
            'items': [{
                'volumeInfo': {
                    'title': 'Test Book',
                    'authors': ['Test Author'],
                    'publishedDate': '2023-01-01',
                    'publisher': 'Test Publisher',
                    'pageCount': 200,
                    'language': 'en',
                    'industryIdentifiers': [{
                        'type': 'ISBN_13',
                        'identifier': '9781234567890'
                    }]
                }
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        metadata = self.plugin._fetch_google_books_metadata('Test Book', 'Test Author')
        
        self.assertEqual(metadata['book_title'], 'Test Book')
        self.assertEqual(metadata['book_author'], 'Test Author')
        self.assertEqual(metadata['published_year'], 2023)
        self.assertEqual(metadata['publisher'], 'Test Publisher')
        self.assertEqual(metadata['page_count'], 200)
        self.assertEqual(metadata['language'], 'en')
        self.assertEqual(metadata['isbn'], '9781234567890')
    
    @patch('requests.get')
    def test_fetch_google_books_metadata_no_results(self, mock_get):
        """Test Google Books API with no results."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'totalItems': 0}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        metadata = self.plugin._fetch_google_books_metadata('Nonexistent Book', 'Unknown Author')
        
        self.assertEqual(metadata, {})
    
    @patch('requests.get')
    def test_fetch_google_books_metadata_api_error(self, mock_get):
        """Test Google Books API error handling."""
        mock_get.side_effect = Exception("API Error")
        
        metadata = self.plugin._fetch_google_books_metadata('Test Book', 'Test Author')
        
        self.assertEqual(metadata, {})


if __name__ == '__main__':
    unittest.main()
