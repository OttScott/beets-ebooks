import unittest
import os
import tempfile
import sys
import subprocess
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Add the parent directory to the path so we can import ebook_manager
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import ebook_manager


class TestEbookManager(unittest.TestCase):
    """Test cases for the ebook_manager.py functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_files = []
        
        # Create test ebook files with various extensions
        test_books = [
            'J.R.R. Tolkien - The Lord of the Rings.epub',
            'Isaac Asimov - Foundation.pdf', 
            'Douglas Adams - Hitchhiker\'s Guide.mobi',
            'Terry Pratchett - Discworld.azw',
            'Ursula K. Le Guin - Left Hand of Darkness.azw3',
            'Frank Herbert - Dune.lrf',
            'Ray Bradbury - Fahrenheit 451.txt',  # Not an ebook
            'Arthur C. Clarke - 2001.mp3',  # Not an ebook
        ]
        
        for book in test_books:
            file_path = os.path.join(self.test_dir, book)
            with open(file_path, 'w') as f:
                f.write(f"Test content for {book}")
            self.test_files.append(file_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.unlink(file_path)
        os.rmdir(self.test_dir)
    
    def test_is_ebook_file_basic(self):
        """Test basic ebook file detection."""
        test_cases = [
            ('book.epub', True),
            ('document.pdf', True),
            ('story.mobi', True),
            ('novel.azw', True),
            ('book.azw3', True),
            ('file.lrf', True),
            ('music.mp3', False),
            ('image.jpg', False),
            ('text.txt', False),
        ]
        
        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = ebook_manager.is_ebook_file(filename)
                self.assertEqual(result, expected, f"Failed for {filename}")
    
    def test_is_ebook_file_with_allowed_extensions(self):
        """Test ebook file detection with custom allowed extensions."""
        # Test with only EPUB allowed
        epub_only = ['.epub']
        self.assertTrue(ebook_manager.is_ebook_file('book.epub', epub_only))
        self.assertFalse(ebook_manager.is_ebook_file('book.pdf', epub_only))
        self.assertFalse(ebook_manager.is_ebook_file('book.mobi', epub_only))
        
        # Test with EPUB and PDF allowed
        epub_pdf = ['.epub', '.pdf']
        self.assertTrue(ebook_manager.is_ebook_file('book.epub', epub_pdf))
        self.assertTrue(ebook_manager.is_ebook_file('book.pdf', epub_pdf))
        self.assertFalse(ebook_manager.is_ebook_file('book.mobi', epub_pdf))
        
        # Test case insensitivity
        self.assertTrue(ebook_manager.is_ebook_file('BOOK.EPUB', epub_only))
        self.assertTrue(ebook_manager.is_ebook_file('Book.Epub', epub_only))
    
    def test_find_ebooks_all_types(self):
        """Test finding all ebook types in directory."""
        ebooks = ebook_manager.find_ebooks(self.test_dir)
        
        # Should find 6 ebook files (excluding .txt and .mp3)
        self.assertEqual(len(ebooks), 6)
        
        # Check that all ebook files are found
        ebook_basenames = [os.path.basename(f) for f in ebooks]
        expected_ebooks = [
            'J.R.R. Tolkien - The Lord of the Rings.epub',
            'Isaac Asimov - Foundation.pdf',
            'Douglas Adams - Hitchhiker\'s Guide.mobi',
            'Terry Pratchett - Discworld.azw',
            'Ursula K. Le Guin - Left Hand of Darkness.azw3',
            'Frank Herbert - Dune.lrf'
        ]
        
        for expected in expected_ebooks:
            self.assertIn(expected, ebook_basenames)
        
        # Should not include non-ebook files
        self.assertNotIn('Ray Bradbury - Fahrenheit 451.txt', ebook_basenames)
        self.assertNotIn('Arthur C. Clarke - 2001.mp3', ebook_basenames)
    
    def test_find_ebooks_with_filtering(self):
        """Test finding ebooks with extension filtering."""
        # Test EPUB only
        epub_files = ebook_manager.find_ebooks(self.test_dir, ['.epub'])
        self.assertEqual(len(epub_files), 1)
        self.assertTrue(epub_files[0].endswith('.epub'))
        
        # Test PDF only
        pdf_files = ebook_manager.find_ebooks(self.test_dir, ['.pdf'])
        self.assertEqual(len(pdf_files), 1)
        self.assertTrue(pdf_files[0].endswith('.pdf'))
        
        # Test EPUB and PDF
        epub_pdf_files = ebook_manager.find_ebooks(self.test_dir, ['.epub', '.pdf'])
        self.assertEqual(len(epub_pdf_files), 2)
        extensions = [os.path.splitext(f)[1].lower() for f in epub_pdf_files]
        self.assertIn('.epub', extensions)
        self.assertIn('.pdf', extensions)
        
        # Test with non-existent extension
        no_files = ebook_manager.find_ebooks(self.test_dir, ['.xyz'])
        self.assertEqual(len(no_files), 0)
    
    def test_parse_extensions(self):
        """Test extension parsing functionality."""
        # Test None input
        result = ebook_manager.parse_extensions(None)
        self.assertIsNone(result)
        
        # Test empty string
        result = ebook_manager.parse_extensions('')
        self.assertIsNone(result)
        
        # Test single extension with dot
        result = ebook_manager.parse_extensions('.epub')
        self.assertEqual(result, ['.epub'])
        
        # Test single extension without dot
        result = ebook_manager.parse_extensions('epub')
        self.assertEqual(result, ['.epub'])
        
        # Test multiple extensions with dots
        result = ebook_manager.parse_extensions('.epub,.pdf,.mobi')
        self.assertEqual(result, ['.epub', '.pdf', '.mobi'])
        
        # Test multiple extensions without dots
        result = ebook_manager.parse_extensions('epub,pdf,mobi')
        self.assertEqual(result, ['.epub', '.pdf', '.mobi'])
        
        # Test mixed case
        result = ebook_manager.parse_extensions('.EPUB,.PDF')
        self.assertEqual(result, ['.epub', '.pdf'])
        
        # Test with spaces
        result = ebook_manager.parse_extensions(' .epub , .pdf , .mobi ')
        self.assertEqual(result, ['.epub', '.pdf', '.mobi'])
    
    @patch('subprocess.run')
    def test_process_ebook_with_beets_success(self, mock_run):
        """Test successful ebook processing with beets."""
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.stdout = "Processing successful"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = ebook_manager.process_ebook_with_beets('test.epub')
        
        self.assertEqual(result, "Processing successful")
        mock_run.assert_called_once_with(
            [ebook_manager.BEETS_EXE, 'ebook', 'test.epub'],
            capture_output=True,
            text=True,
            check=True
        )
    
    @patch('subprocess.run')
    def test_process_ebook_with_beets_error(self, mock_run):
        """Test ebook processing error handling."""
        # Mock subprocess error
        mock_run.side_effect = subprocess.CalledProcessError(1, 'beet')
        
        with patch('builtins.print') as mock_print:
            result = ebook_manager.process_ebook_with_beets('test.epub')
        
        self.assertIsNone(result)
        mock_print.assert_called()
    
    @patch('subprocess.run')
    def test_import_ebook_to_beets_success(self, mock_run):
        """Test successful ebook import to beets."""
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.stdout = "Successfully imported ebook"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = ebook_manager.import_ebook_to_beets('test.epub')
        
        self.assertEqual(result, "Successfully imported ebook")
        # Should use absolute path
        expected_path = os.path.abspath('test.epub')
        mock_run.assert_called_once_with(
            [ebook_manager.BEETS_EXE, 'import-ebooks', expected_path],
            capture_output=True,
            text=True,
            check=True
        )
    
    @patch('ebook_manager.find_ebooks')
    @patch('builtins.print')
    def test_scan_collection_with_filtering(self, mock_print, mock_find):
        """Test collection scanning with extension filtering."""
        # Mock finding 2 EPUB files
        mock_find.return_value = ['book1.epub', 'book2.epub']
        
        with patch('ebook_manager.process_ebook_with_beets') as mock_process:
            mock_process.return_value = "Processed successfully"
            ebook_manager.scan_collection(self.test_dir, ['.epub'])
        
        # Check that find_ebooks was called with filtering
        mock_find.assert_called_once_with(self.test_dir, ['.epub'])
        
        # Check that filtering message was printed
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        self.assertTrue(any('Filtering by extensions: [' in call for call in print_calls))
    
    @patch('ebook_manager.find_ebooks')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_import_collection_with_filtering(self, mock_print, mock_input, mock_find):
        """Test collection import with extension filtering."""
        # Mock user input and found files
        mock_input.return_value = 'y'
        mock_find.return_value = ['book1.epub', 'book2.epub']
        
        with patch('ebook_manager.import_ebook_to_beets') as mock_import:
            mock_import.return_value = "Successfully imported ebook"
            ebook_manager.import_collection(self.test_dir, ['.epub'])
        
        # Check that find_ebooks was called with filtering
        mock_find.assert_called_once_with(self.test_dir, ['.epub'])
        
        # Check that import was called for each file
        self.assertEqual(mock_import.call_count, 2)
    
    @patch('ebook_manager.find_ebooks')
    @patch('builtins.input')
    @patch('subprocess.run')
    def test_batch_import_with_filtering(self, mock_run, mock_input, mock_find):
        """Test batch import with extension filtering uses individual imports."""
        # Mock user input and found files
        mock_input.return_value = 'y'
        mock_find.return_value = ['book1.epub', 'book2.epub']
        
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.stdout = "Successfully imported ebook"
        mock_run.return_value = mock_result
        
        with patch('builtins.print'):
            ebook_manager.batch_import_ebooks(self.test_dir, ['.epub'])
        
        # When filtering, should use individual imports (2 calls)
        self.assertEqual(mock_run.call_count, 2)
        
        # Check that each call uses import-ebooks with individual files
        for call in mock_run.call_args_list:
            args = call[0][0]  # Get the command arguments
            self.assertEqual(args[1], 'import-ebooks')
            self.assertTrue(args[2].endswith('.epub'))
    
    @patch('ebook_manager.find_ebooks')
    @patch('builtins.input')
    @patch('subprocess.run')
    def test_batch_import_without_filtering(self, mock_run, mock_input, mock_find):
        """Test batch import without filtering uses directory import."""
        # Mock user input and found files
        mock_input.return_value = 'y'
        mock_find.return_value = ['book1.epub', 'book2.pdf']
        
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.stdout = "Batch import successful"
        mock_run.return_value = mock_result
        
        with patch('builtins.print'):
            ebook_manager.batch_import_ebooks(self.test_dir, None)
        
        # When not filtering, should use directory import (1 call)
        self.assertEqual(mock_run.call_count, 1)
        
        # Check that it uses the directory path
        args = mock_run.call_args[0][0]
        self.assertEqual(args[1], 'import-ebooks')
        self.assertEqual(args[2], os.path.abspath(self.test_dir))
    
    def test_extension_filtering_integration(self):
        """Integration test for extension filtering across all functions."""
        # Test that all functions correctly use extension filtering
        
        # Test with EPUB only
        epub_files = ebook_manager.find_ebooks(self.test_dir, ['.epub'])
        self.assertEqual(len(epub_files), 1)
        self.assertTrue(all(f.endswith('.epub') for f in epub_files))
        
        # Test with multiple extensions
        multi_files = ebook_manager.find_ebooks(self.test_dir, ['.epub', '.pdf', '.mobi'])
        self.assertEqual(len(multi_files), 3)
        
        # Test that filtering affects different functions consistently
        for allowed_ext in [['.epub'], ['.pdf'], ['.epub', '.pdf']]:
            files_found = ebook_manager.find_ebooks(self.test_dir, allowed_ext)
            
            # All found files should match the allowed extensions
            for file_path in files_found:
                file_ext = os.path.splitext(file_path)[1].lower()
                self.assertIn(file_ext, allowed_ext)
    
    def test_case_insensitive_extension_matching(self):
        """Test that extension matching is case insensitive."""
        # Create test files with mixed case extensions
        mixed_case_dir = tempfile.mkdtemp()
        mixed_files = []
        
        try:
            test_books = [
                'book1.EPUB',
                'book2.Pdf', 
                'book3.MoBi',
            ]
            
            for book in test_books:
                file_path = os.path.join(mixed_case_dir, book)
                with open(file_path, 'w') as f:
                    f.write(f"Test content for {book}")
                mixed_files.append(file_path)
            
            # Test that lowercase filter matches uppercase files
            epub_files = ebook_manager.find_ebooks(mixed_case_dir, ['.epub'])
            self.assertEqual(len(epub_files), 1)
            self.assertTrue(epub_files[0].endswith('.EPUB'))
            
            # Test that mixed case filters work (input gets normalized)
            # Using mixed case input that gets normalized to lowercase
            mixed_case_extensions = ebook_manager.parse_extensions('.EPUB,.Pdf,.MoBi')
            all_files = ebook_manager.find_ebooks(mixed_case_dir, mixed_case_extensions)
            self.assertEqual(len(all_files), 3)
            
        finally:
            for file_path in mixed_files:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            os.rmdir(mixed_case_dir)
    
    def test_extract_book_identifier(self):
        """Test extracting book identifiers for grouping."""
        test_cases = [
            ('Douglas Adams - The Hitchhiker\'s Guide to the Galaxy.epub', 
             'douglas adams - the hitchhiker\'s guide to the galaxy'),
            ('J.R.R. Tolkien - The Lord of the Rings (1).pdf',
             'j.r.r. tolkien - the lord of the rings'),
            ('Isaac Asimov - Foundation [2005].mobi',
             'isaac asimov - foundation'),
            ('Terry Pratchett - Discworld.azw',
             'terry pratchett - discworld'),
            ('single_word_title.epub', 'single_word_title'),  # Fallback case
        ]
        
        for filepath, expected in test_cases:
            with self.subTest(filepath=filepath):
                result = ebook_manager.extract_book_identifier(filepath)
                self.assertEqual(result, expected)
    
    def test_filter_onefile_per_book(self):
        """Test filtering to keep only one file per book."""
        # Create test files for duplicate books
        temp_dir = tempfile.mkdtemp()
        file_paths = []
        try:
            test_files = [
                'Douglas Adams - The Hitchhiker\'s Guide to the Galaxy.epub',
                'Douglas Adams - The Hitchhiker\'s Guide to the Galaxy.mobi', 
                'Douglas Adams - The Hitchhiker\'s Guide to the Galaxy.pdf',
                'Isaac Asimov - Foundation.pdf',
                'J.R.R. Tolkien - The Lord of the Rings.epub',
                'J.R.R. Tolkien - The Lord of the Rings.mobi',
            ]
            
            for filename in test_files:
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(f"Content for {filename}")
                file_paths.append(filepath)
            
            # Test filtering
            filtered = ebook_manager.filter_onefile_per_book(file_paths)
            
            # Should keep only highest priority format per book
            filtered_names = [os.path.basename(f) for f in filtered]
            
            # Expected: epub (highest) for duplicates, pdf for Foundation (only one)
            expected_names = [
                'Douglas Adams - The Hitchhiker\'s Guide to the Galaxy.epub',
                'Isaac Asimov - Foundation.pdf',
                'J.R.R. Tolkien - The Lord of the Rings.epub',
            ]
            
            self.assertEqual(len(filtered), 3)
            for expected in expected_names:
                self.assertIn(expected, filtered_names)
                
        finally:
            # Cleanup
            for filepath in file_paths:
                if os.path.exists(filepath):
                    os.unlink(filepath)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
    
    def test_format_priority(self):
        """Test that format priority is applied correctly."""
        formats_by_priority = ['.epub', '.mobi', '.azw', '.azw3', '.pdf', '.lrf']
        
        for i, format1 in enumerate(formats_by_priority):
            for j, format2 in enumerate(formats_by_priority):
                if i < j:  # format1 should have higher priority than format2
                    priority1 = ebook_manager.FORMAT_PRIORITY.get(format1, 0)
                    priority2 = ebook_manager.FORMAT_PRIORITY.get(format2, 0)
                    self.assertGreater(priority1, priority2, 
                        f"{format1} should have higher priority than {format2}")


class TestEbookManagerCLI(unittest.TestCase):
    """Test cases for the ebook_manager CLI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test ebook file
        self.test_file = os.path.join(self.test_dir, 'test.epub')
        with open(self.test_file, 'w') as f:
            f.write("Test epub content")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)
        os.rmdir(self.test_dir)
    
    @patch('sys.argv')
    @patch('builtins.print')
    def test_main_no_arguments(self, mock_print, mock_argv):
        """Test main function with no arguments shows help."""
        mock_argv.__getitem__.side_effect = lambda x: ['ebook_manager.py'][x]
        mock_argv.__len__.return_value = 1
        
        ebook_manager.main()
        
        # Should print help information
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        self.assertTrue(any('Ebook Collection Manager' in call for call in print_calls))
        self.assertTrue(any('--ext' in call for call in print_calls))
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch('ebook_manager.scan_collection')
    def test_main_scan_command(self, mock_scan, mock_parse_args):
        """Test main function with scan command."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.command = 'scan'
        mock_args.path = self.test_dir
        mock_args.ext = '.epub'
        mock_args.onefile = False
        mock_parse_args.return_value = mock_args
        
        with patch('os.path.isdir', return_value=True):
            ebook_manager.main()
        
        # Should call scan_collection with parsed extensions
        mock_scan.assert_called_once_with(self.test_dir, ['.epub'], False)
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch('ebook_manager.import_collection')
    def test_main_import_command_with_multiple_extensions(self, mock_import, mock_parse_args):
        """Test main function with import command and multiple extensions."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.command = 'import'
        mock_args.path = self.test_dir
        mock_args.ext = '.epub,.pdf,.mobi'
        mock_args.onefile = False
        mock_parse_args.return_value = mock_args
        
        with patch('os.path.isdir', return_value=True):
            ebook_manager.main()
        
        # Should call import_collection with parsed extensions
        mock_import.assert_called_once_with(self.test_dir, ['.epub', '.pdf', '.mobi'], False)
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch('builtins.print')
    def test_main_invalid_directory(self, mock_print, mock_parse_args):
        """Test main function with invalid directory path."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.command = 'scan'
        mock_args.path = '/nonexistent/directory'
        mock_args.ext = None
        mock_parse_args.return_value = mock_args
        
        ebook_manager.main()
        
        # Should print error message
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        self.assertTrue(any('Directory not found' in call for call in print_calls))
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch('ebook_manager.scan_collection')  
    def test_main_scan_command_with_onefile(self, mock_scan, mock_parse_args):
        """Test main function with scan command and --onefile option."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.command = 'scan'
        mock_args.path = self.test_dir
        mock_args.ext = '.epub,.pdf'
        mock_args.onefile = True
        mock_parse_args.return_value = mock_args
        
        with patch('os.path.isdir', return_value=True):
            ebook_manager.main()
        
        # Should call scan_collection with extensions and onefile=True
        mock_scan.assert_called_once_with(self.test_dir, ['.epub', '.pdf'], True)
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch('ebook_manager.import_collection')
    def test_main_import_command_with_onefile(self, mock_import, mock_parse_args):
        """Test main function with import command and --onefile option."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.command = 'import'
        mock_args.path = self.test_dir
        mock_args.ext = None
        mock_args.onefile = True
        mock_parse_args.return_value = mock_args
        
        with patch('os.path.isdir', return_value=True):
            ebook_manager.main()
        
        # Should call import_collection with onefile=True
        mock_import.assert_called_once_with(self.test_dir, None, True)
    
    @patch('argparse.ArgumentParser.parse_args') 
    @patch('ebook_manager.batch_import_ebooks')
    def test_main_batch_import_with_onefile_and_ext(self, mock_batch_import, mock_parse_args):
        """Test main function with batch-import command using both --onefile and --ext."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.command = 'batch-import'
        mock_args.path = self.test_dir
        mock_args.ext = '.epub'
        mock_args.onefile = True
        mock_parse_args.return_value = mock_args
        
        with patch('os.path.isdir', return_value=True):
            ebook_manager.main()
        
        # Should call batch_import_ebooks with both extensions and onefile=True
        mock_batch_import.assert_called_once_with(self.test_dir, ['.epub'], True)


if __name__ == '__main__':
    unittest.main()
