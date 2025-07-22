import os
import json
import logging

# Set up logging
logger = logging.getLogger('beets.ebooks')

try:
    from beets.plugins import BeetsPlugin
    from beets import library
    from beets.dbcore import types
    from beets.importer import ImportTask
    import beets.ui
    import beets.util
    from beets.library import Item
    BEETS_AVAILABLE = True
except ImportError:
    # Beets not installed - this is expected during development
    BEETS_AVAILABLE = False
    
    # Create mock classes for development
    class BeetsPlugin:
        item_types = {}
        def __init__(self):
            self.config = MockConfig()
        def register_listener(self, event, func):
            pass
    
    class MockConfig:
        def add(self, config_dict):
            self._config = config_dict
        def get(self):
            return []
        def keys(self):
            return self._config.keys() if hasattr(self, '_config') else []

try:
    import requests
except ImportError:
    requests = None

try:
    import ebooklib
    from ebooklib import epub
except ImportError:
    ebooklib = None
    epub = None


class EBooksPlugin(BeetsPlugin):
    """Beets plugin for managing ebook collections."""
    
    item_types = {
        'book_author': types.String() if BEETS_AVAILABLE else str,
        'book_title': types.String() if BEETS_AVAILABLE else str,
        'isbn': types.String() if BEETS_AVAILABLE else str,
        'published_year': types.Integer() if BEETS_AVAILABLE else int,
        'publisher': types.String() if BEETS_AVAILABLE else str,
        'page_count': types.Integer() if BEETS_AVAILABLE else int,
        'language': types.String() if BEETS_AVAILABLE else str,
        'file_format': types.String() if BEETS_AVAILABLE else str,
        'ebook': types.Boolean() if BEETS_AVAILABLE else bool,  # Flag to identify ebooks
        # Comic-specific fields
        'series': types.String() if BEETS_AVAILABLE else str,
        'issue_number': types.Integer() if BEETS_AVAILABLE else int,
        'genre': types.String() if BEETS_AVAILABLE else str,
        'summary': types.String() if BEETS_AVAILABLE else str,
    }

    def __init__(self):
        super().__init__()
        self.config.add({
            'google_api_key': '',
            'download_covers': True,
            'ebook_extensions': ['.epub', '.pdf', '.mobi', '.lrf', '.azw', '.azw3', '.cbr', '.cbz'],
            'metadata_sources': ['google_books', 'open_library'],
            'auto_import': True,  # Automatically import ebooks during beet import
        })

    def import_task_files_hook(self, session, task):
        """Hook called during import to handle ebook files."""
        if not hasattr(task, 'paths'):
            return
            
        ebook_paths = []
        non_ebook_paths = []
        
        # Separate ebook files from regular files
        for path in task.paths:
            if os.path.isfile(path) and self._is_ebook_file(path):
                ebook_paths.append(path)
            else:
                non_ebook_paths.append(path)
        
        # If we found ebooks, process them
        if ebook_paths:
            logger.info(f"Found {len(ebook_paths)} ebook(s) to import")
            for ebook_path in ebook_paths:
                self._import_ebook_to_library(ebook_path, session.lib)
                
            # Remove ebook paths from the task so beets doesn't try to process them as music
            task.paths = non_ebook_paths

    def _import_ebook_to_library(self, file_path, lib):
        """Import an ebook file into the beets library."""
        try:
            logger.info(f"Importing ebook: {file_path}")
            
            # Ensure we have an absolute path
            file_path = os.path.abspath(file_path)
            
            # Extract metadata - create a fresh copy for each file
            metadata = self._extract_basic_metadata(file_path)
            
            # Enrich with external metadata
            if metadata.get('book_title') or metadata.get('book_author'):
                external_metadata = self._fetch_external_metadata(
                    metadata.get('book_title', ''),
                    metadata.get('book_author', '')
                )
                # Create a new dict to avoid modifying cached metadata
                metadata = dict(metadata)
                metadata.update(external_metadata)
            
            # Create a beets library item - fresh instance for each file
            item = Item()
            
            # Map ebook metadata to beets fields
            # Use title and artist fields that beets expects, plus our custom fields
            item.title = metadata.get('book_title', os.path.splitext(os.path.basename(file_path))[0])
            item.artist = metadata.get('book_author', 'Unknown Author')
            item.album = metadata.get('book_title', item.title)
            item.albumartist = item.artist
            
            # Set our custom ebook fields - ensure we're using the correct metadata
            item.book_author = metadata.get('book_author', '')
            item.book_title = metadata.get('book_title', '')
            item.isbn = metadata.get('isbn', '')
            item.published_year = metadata.get('published_year', 0)
            item.publisher = metadata.get('publisher', '')
            item.page_count = metadata.get('page_count', 0)
            item.language = metadata.get('language', '')
            item.file_format = metadata.get('file_format', '')
            item.ebook = True  # Flag to identify this as an ebook
            
            # Set comic-specific fields if available
            item.series = metadata.get('series', '')
            item.issue_number = metadata.get('issue_number', 0)
            item.genre = metadata.get('genre', '')
            item.summary = metadata.get('summary', '')
            
            # Set file path and basic properties - ensure correct path assignment
            item.path = beets.util.bytestring_path(file_path)
            item.length = 0  # Ebooks don't have length in seconds
            item.bitrate = 0
            item.format = metadata.get('file_format', '').lower()
            
            # Verify the item has the correct path before adding
            if not os.path.exists(file_path):
                logger.error(f"File does not exist: {file_path}")
                return None
            
            # Add to library
            lib.add(item)
            logger.info(f"Added ebook to library: {item.artist} - {item.title}")
            
            return item
            
        except Exception as e:
            logger.error(f"Error importing ebook {file_path}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def _is_ebook_file(self, filename):
        """Check if a file is an ebook based on its extension."""
        try:
            extensions = self.config['ebook_extensions'].get()
            if extensions is None:
                extensions = ['.epub', '.pdf', '.mobi', '.lrf', '.azw', '.azw3', '.cbr', '.cbz']
            return any(filename.lower().endswith(ext) for ext in extensions)
        except Exception:
            # Fallback for development mode
            default_extensions = ['.epub', '.pdf', '.mobi', '.lrf', '.azw', '.azw3', '.cbr', '.cbz']
            return any(filename.lower().endswith(ext) for ext in default_extensions)

    def import_hook(self, session, task):
        """Hook called when an import task starts."""
        if hasattr(task, 'is_ebook') and task.is_ebook:
            logger.info(f"Processing ebook import task: {task.paths}")
            self._enrich_ebook_metadata(task)

    def _enrich_ebook_metadata(self, task):
        """Enrich ebook metadata using external sources."""
        for path in task.paths:
            if os.path.isfile(path):
                try:
                    metadata = self._extract_basic_metadata(path)
                    
                    # Try to get additional metadata from external sources
                    if metadata.get('title') or metadata.get('author'):
                        external_metadata = self._fetch_external_metadata(
                            metadata.get('title', ''),
                            metadata.get('author', '')
                        )
                        metadata.update(external_metadata)
                    
                    # Create or update library item
                    self._create_library_item(path, metadata)
                    
                except Exception as e:
                    logger.error(f"Error processing ebook {path}: {e}")

    def _extract_basic_metadata(self, file_path):
        """Extract basic metadata from ebook file."""
        metadata = {
            'file_format': os.path.splitext(file_path)[1][1:].upper(),
            'path': file_path,
        }
        
        filename = os.path.basename(file_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        # Try to parse filename for basic info
        # Handle comic book naming conventions (e.g., "Batman - Detective Comics 001")
        if file_path.lower().endswith(('.cbr', '.cbz')):
            metadata.update(self._parse_comic_filename(name_without_ext))
        elif ' - ' in name_without_ext:
            # Standard ebook format: "Author - Title" or "Title - Author"
            parts = name_without_ext.split(' - ', 1)
            if len(parts) == 2:
                part1, part2 = parts[0].strip(), parts[1].strip()
                
                # Heuristic: If part2 looks like a person's name (has capitalized words,
                # common name patterns), assume "Title - Author" format
                # Otherwise assume "Author - Title" format
                author_indicators = ['Child', 'Smith', 'Brown', 'King', 'Lee', 'Martin', 'Johnson']
                title_indicators = ['The ', 'A ', 'An ']
                
                if (any(indicator in part2 for indicator in author_indicators) or
                    (len(part2.split()) <= 3 and part2.title() == part2) or
                    any(part1.startswith(indicator) for indicator in title_indicators)):
                    # Likely "Title - Author" format
                    metadata['book_title'] = part1
                    metadata['book_author'] = part2
                else:
                    # Assume "Author - Title" format
                    metadata['book_author'] = part1
                    metadata['book_title'] = part2
        else:
            metadata['book_title'] = name_without_ext.strip()
        
        # Try to extract format-specific metadata
        if file_path.lower().endswith('.epub'):
            try:
                epub_metadata = self._extract_epub_metadata(file_path)
                metadata.update(epub_metadata)
            except Exception as e:
                logger.warning(f"Could not extract EPUB metadata from {file_path}: {e}")
        elif file_path.lower().endswith(('.cbr', '.cbz')):
            try:
                comic_metadata = self._extract_comic_metadata(file_path)
                metadata.update(comic_metadata)
            except Exception as e:
                logger.warning(f"Could not extract comic metadata from {file_path}: {e}")
        
        return metadata

    def _parse_comic_filename(self, name_without_ext):
        """Parse comic book filename for series, title, and issue information."""
        metadata = {}
        
        # Common comic naming patterns:
        # "Batman - Detective Comics 001"
        # "Spider-Man - Amazing Spider-Man 15"
        # "X-Men - Uncanny X-Men 001"
        
        if ' - ' in name_without_ext:
            parts = name_without_ext.split(' - ', 1)
            if len(parts) == 2:
                series_part, title_issue_part = parts[0].strip(), parts[1].strip()
                
                # Try to extract issue number from the end
                import re
                issue_match = re.search(r'(\d+)$', title_issue_part)
                if issue_match:
                    issue_number = int(issue_match.group(1))
                    title_part = title_issue_part[:issue_match.start()].strip()
                    
                    metadata['series'] = series_part
                    metadata['book_title'] = title_part if title_part else series_part
                    metadata['issue_number'] = issue_number
                    metadata['book_author'] = f"{series_part} #{issue_number:03d}"
                else:
                    # No issue number found, treat normally
                    metadata['series'] = series_part
                    metadata['book_title'] = title_issue_part
                    metadata['book_author'] = series_part
        else:
            metadata['book_title'] = name_without_ext
        
        return metadata

    def _extract_epub_metadata(self, file_path):
        """Extract metadata from EPUB file using ebooklib."""
        try:
            import ebooklib
            from ebooklib import epub
            
            book = epub.read_epub(file_path)
            metadata = {}
            
            # Extract title
            title = book.get_metadata('DC', 'title')
            if title:
                metadata['book_title'] = title[0][0]
            
            # Extract author
            creator = book.get_metadata('DC', 'creator')
            if creator:
                metadata['book_author'] = creator[0][0]
            
            # Extract language
            language = book.get_metadata('DC', 'language')
            if language:
                metadata['language'] = language[0][0]
            
            # Extract publisher
            publisher = book.get_metadata('DC', 'publisher')
            if publisher:
                metadata['publisher'] = publisher[0][0]
            
            # Extract date/year
            date = book.get_metadata('DC', 'date')
            if date:
                try:
                    year = int(date[0][0][:4])
                    metadata['published_year'] = year
                except (ValueError, IndexError):
                    pass
            
            # Extract ISBN
            identifier = book.get_metadata('DC', 'identifier')
            for ident in identifier:
                # ident[1] might be None, a string, or a dict - handle safely
                identifier_type = ident[1] if len(ident) > 1 else None
                if identifier_type and isinstance(identifier_type, str) and 'isbn' in identifier_type.lower():
                    metadata['isbn'] = ident[0]
                    break
            
            return metadata
            
        except ImportError:
            logger.warning("ebooklib not available, cannot extract EPUB metadata")
            return {}
        except Exception as e:
            logger.error(f"Error extracting EPUB metadata: {e}")
            return {}

    def _extract_comic_metadata(self, file_path):
        """Extract metadata from CBR/CBZ comic files."""
        try:
            import zipfile
        except ImportError:
            logger.warning("zipfile not available, cannot extract comic metadata")
            return {}
            
        # Try to import rarfile for CBR support, but don't fail if it's not available
        try:
            import rarfile
            RARFILE_AVAILABLE = True
        except ImportError:
            RARFILE_AVAILABLE = False
            
        metadata = {}
        is_cbz = file_path.lower().endswith('.cbz')
        is_cbr = file_path.lower().endswith('.cbr')
        
        # Basic comic detection - count image files
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        page_count = 0
        
        if is_cbz:
            try:
                with zipfile.ZipFile(file_path, 'r') as comic_zip:
                    # Count image files
                    for name in comic_zip.namelist():
                        if name.lower().endswith(image_extensions) and not name.startswith('__MACOSX/'):
                            page_count += 1
                    
                    # Look for ComicInfo.xml metadata
                    try:
                        comic_info = comic_zip.read('ComicInfo.xml')
                        comic_metadata = self._parse_comic_info_xml(comic_info)
                        metadata.update(comic_metadata)
                    except KeyError:
                        # No ComicInfo.xml found
                        pass
            except Exception as e:
                logger.warning(f"Error reading CBZ file {file_path}: {e}")
                
        elif is_cbr and RARFILE_AVAILABLE:
            try:
                with rarfile.RarFile(file_path, 'r') as comic_rar:
                    # Count image files
                    for info in comic_rar.infolist():
                        if info.filename.lower().endswith(image_extensions):
                            page_count += 1
                    
                    # Look for ComicInfo.xml metadata
                    try:
                        comic_info = comic_rar.read('ComicInfo.xml')
                        comic_metadata = self._parse_comic_info_xml(comic_info)
                        metadata.update(comic_metadata)
                    except Exception:
                        # No ComicInfo.xml found or error reading
                        pass
            except Exception as e:
                logger.warning(f"Error reading CBR file {file_path}: {e}")
        elif is_cbr and not RARFILE_AVAILABLE:
            logger.warning("rarfile not available, cannot extract CBR metadata")
            
        if page_count > 0:
            metadata['page_count'] = page_count
            
        # Set format-specific metadata
        metadata['file_format'] = 'CBZ' if is_cbz else 'CBR'
        
        return metadata

    def _parse_comic_info_xml(self, xml_content):
        """Parse ComicInfo.xml metadata from comic files."""
        try:
            import xml.etree.ElementTree as ET
            
            metadata = {}
            root = ET.fromstring(xml_content)
            
            # Extract common comic metadata fields
            field_mapping = {
                'Title': 'book_title',
                'Writer': 'book_author',
                'Series': 'series',
                'Number': 'issue_number',
                'Year': 'published_year',
                'Publisher': 'publisher',
                'PageCount': 'page_count',
                'Summary': 'summary',
                'Genre': 'genre',
                'LanguageISO': 'language',
            }
            
            for xml_field, metadata_field in field_mapping.items():
                element = root.find(xml_field)
                if element is not None and element.text:
                    value = element.text.strip()
                    
                    # Convert numeric fields
                    if metadata_field in ['published_year', 'page_count', 'issue_number']:
                        try:
                            value = int(value)
                        except ValueError:
                            continue
                    
                    metadata[metadata_field] = value
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Error parsing ComicInfo.xml: {e}")
            return {}

    def _fetch_external_metadata(self, title, author):
        """Fetch metadata from external sources."""
        metadata = {}
        
        sources = self.config['metadata_sources'].get()
        
        if 'google_books' in sources:
            try:
                google_metadata = self._fetch_google_books_metadata(title, author)
                metadata.update(google_metadata)
            except Exception as e:
                logger.warning(f"Error fetching Google Books metadata: {e}")
        
        return metadata

    def _fetch_google_books_metadata(self, title, author):
        """Fetch metadata from Google Books API."""
        api_key = self.config['google_api_key'].get()
        
        # Build search query
        query_parts = []
        if title:
            query_parts.append(f'intitle:"{title}"')
        if author:
            query_parts.append(f'inauthor:"{author}"')
        
        if not query_parts:
            return {}
        
        query = '+'.join(query_parts)
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        
        if api_key:
            url += f"&key={api_key}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('totalItems', 0) > 0:
                book_info = data['items'][0]['volumeInfo']
                metadata = {}
                
                if 'title' in book_info:
                    metadata['book_title'] = book_info['title']
                
                if 'authors' in book_info:
                    metadata['book_author'] = ', '.join(book_info['authors'])
                
                if 'publishedDate' in book_info:
                    try:
                        year = int(book_info['publishedDate'][:4])
                        metadata['published_year'] = year
                    except (ValueError, IndexError):
                        pass
                
                if 'publisher' in book_info:
                    metadata['publisher'] = book_info['publisher']
                
                if 'pageCount' in book_info:
                    metadata['page_count'] = book_info['pageCount']
                
                if 'language' in book_info:
                    metadata['language'] = book_info['language']
                
                # Look for ISBN
                if 'industryIdentifiers' in book_info:
                    for identifier in book_info['industryIdentifiers']:
                        if identifier['type'] in ['ISBN_10', 'ISBN_13']:
                            metadata['isbn'] = identifier['identifier']
                            break
                
                return metadata
            
        except Exception as e:
            logger.error(f"Error fetching from Google Books API: {e}")
        
        return {}

    def _create_library_item(self, file_path, metadata):
        """Create or update a library item for the ebook."""
        # This is a simplified version - in a real implementation,
        # you'd want to integrate more closely with Beets' library system
        logger.info(f"Would create library item for {file_path} with metadata: {metadata}")
        
        # For now, just log the metadata that would be stored
        for key, value in metadata.items():
            if value:
                logger.info(f"  {key}: {value}")

    def commands(self):
        """Return command-line commands provided by this plugin."""
        
        def ebook_func(lib, opts, args):
            """Handle the 'ebook' command - display metadata only."""
            if args:
                paths = args
            else:
                print("Usage: beet ebook <path> [<path> ...]")
                return
            
            for path in paths:
                if os.path.isfile(path) and self._is_ebook_file(path):
                    print(f"Processing ebook: {path}")
                    metadata = self._extract_basic_metadata(path)
                    
                    # Display extracted metadata
                    print("Extracted metadata:")
                    for key, value in metadata.items():
                        if value:
                            print(f"  {key}: {value}")
                    
                    # Try to fetch external metadata
                    if metadata.get('book_title') or metadata.get('book_author'):
                        print("\nFetching external metadata...")
                        external_metadata = self._fetch_external_metadata(
                            metadata.get('book_title', ''),
                            metadata.get('book_author', '')
                        )
                        if external_metadata:
                            print("External metadata:")
                            for key, value in external_metadata.items():
                                if value and key not in metadata:
                                    print(f"  {key}: {value}")
                else:
                    print(f"Skipping non-ebook file: {path}")
        
        def import_ebooks_func(lib, opts, args):
            """Handle the 'import-ebooks' command - actually import to beets library."""
            if args:
                paths = args
            else:
                print("Usage: beet import-ebooks <path> [<path> ...]")
                print("This command imports ebooks into your beets library.")
                return
            
            imported_count = 0
            for path in paths:
                if os.path.isdir(path):
                    # Process directory
                    for root, _, files in os.walk(path):
                        for file in files:
                            if self._is_ebook_file(file):
                                full_path = os.path.join(root, file)
                                item = self._import_ebook_to_library(full_path, lib)
                                if item:
                                    imported_count += 1
                                    print(f"[OK] Imported: {item.artist} - {item.title}")
                elif os.path.isfile(path) and self._is_ebook_file(path):
                    # Process single file
                    item = self._import_ebook_to_library(path, lib)
                    if item:
                        imported_count += 1
                        print(f"[OK] Imported: {item.artist} - {item.title}")
                else:
                    print(f"[ERROR] Skipping non-ebook: {path}")
            
            if imported_count > 0:
                print(f"\n[SUCCESS] Successfully imported {imported_count} ebook(s) to your beets library!")
                print("You can now use:")
                print("  beet ls ebook:true")
                print("  beet ls book_author:tolkien")
                print("  beet ls book_title:'lord of the rings'")
            else:
                print("[ERROR] No ebooks were imported.")
        
        # Create commands
        try:
            import beets.ui
            ebook_cmd = beets.ui.Subcommand('ebook', help='display ebook metadata')
            ebook_cmd.func = ebook_func
            
            import_cmd = beets.ui.Subcommand('import-ebooks', help='import ebooks into beets library')
            import_cmd.func = import_ebooks_func
            
            return [ebook_cmd, import_cmd]
        except ImportError:
            # beets.ui not available (development mode)
            return []

    def album_distance(self, items, album_info, mapping):
        """Return a distance for ebooks (always a high distance to prefer manual import)."""
        return 1.0

    def track_distance(self, item, track_info):
        """Return a distance for individual ebooks."""
        return 1.0

    def import_stage(self, session, task):
        """Handle ebook import during beets import process."""
        # Check if any of the paths contain ebooks
        ebook_paths = []
        if hasattr(task, 'paths'):
            for path in task.paths:
                if os.path.isdir(path):
                    for root, _, files in os.walk(path):
                        for file in files:
                            if self._is_ebook_file(file):
                                ebook_paths.append(os.path.join(root, file))
                elif os.path.isfile(path) and self._is_ebook_file(path):
                    ebook_paths.append(path)
        
        if ebook_paths:
            logger.info(f"Found {len(ebook_paths)} ebook(s) during import")
            for ebook_path in ebook_paths:
                self._process_ebook_import(ebook_path, session)

    def _process_ebook_import(self, file_path, session):
        """Process a single ebook file for import."""
        try:
            logger.info(f"Processing ebook: {file_path}")
            metadata = self._extract_basic_metadata(file_path)
            
            # Try to get additional metadata from external sources
            if metadata.get('book_title') or metadata.get('book_author'):
                external_metadata = self._fetch_external_metadata(
                    metadata.get('book_title', ''),
                    metadata.get('book_author', '')
                )
                metadata.update(external_metadata)
            
            # For now, just log what would be imported
            logger.info(f"Would import ebook with metadata: {metadata}")
            
            # You could extend this to actually create library items here
            
        except Exception as e:
            logger.error(f"Error processing ebook {file_path}: {e}")
