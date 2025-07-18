import os
import json
import logging

try:
    from beets.plugins import BeetsPlugin
    from beets import library
    from beets.dbcore import types
    from beets.importer import ImportTask
    import beets.ui
except ImportError:
    # Beets not installed - this is expected during development
    pass

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

# Set up logging
logger = logging.getLogger('beets.ebooks')


class EbookImportTask(ImportTask):
    """Custom import task for ebook files."""
    
    def __init__(self, paths, session):
        super().__init__(paths, session)
        self.is_ebook = True
        
    def lookup_candidates(self):
        """Override to provide ebook-specific lookup logic."""
        return []


class EBooksPlugin(BeetsPlugin):
    """Beets plugin for managing ebook collections."""
    
    item_types = {
        'book_author': types.String(),
        'book_title': types.String(),
        'isbn': types.String(),
        'published_year': types.Integer(),
        'publisher': types.String(),
        'page_count': types.Integer(),
        'language': types.String(),
        'file_format': types.String(),
    }

    def __init__(self):
        super().__init__()
        self.config.add({
            'google_api_key': '',
            'download_covers': True,
            'ebook_extensions': ['.epub', '.pdf', '.mobi', '.lrf', '.azw', '.azw3'],
            'metadata_sources': ['google_books', 'open_library'],
        })

        # Patch Beets' task discovery to include ebooks
        self._patch_read_tasks()

        # Hook for metadata enrichment
        self.register_listener('import_task_start', self.import_hook)

    def _patch_read_tasks(self):
        """Monkey-patch beets.importer.stages.read_tasks to add ebooks."""
        import beets.importer.stages as stages

        original_read_tasks = stages.read_tasks

        def custom_read_tasks(session, paths):
            # Yield all normal tasks first
            for task in original_read_tasks(session, paths):
                yield task

            # Add ebook tasks
            for path in paths:
                for root, _, files in os.walk(path):
                    for file in files:
                        if self._is_ebook_file(file):
                            full_path = os.path.join(root, file)
                            logger.info(f"Found ebook: {full_path}")
                            yield EbookImportTask([full_path], session)

        stages.read_tasks = custom_read_tasks

    def _is_ebook_file(self, filename):
        """Check if a file is an ebook based on its extension."""
        extensions = self.config['ebook_extensions'].get()
        return any(filename.lower().endswith(ext) for ext in extensions)

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
        # Format: "Author - Title" or "Title - Author" or just "Title"
        if ' - ' in name_without_ext:
            parts = name_without_ext.split(' - ', 1)
            if len(parts) == 2:
                # Assume first part is author, second is title
                metadata['book_author'] = parts[0].strip()
                metadata['book_title'] = parts[1].strip()
        else:
            metadata['book_title'] = name_without_ext.strip()
        
        # Try to extract from EPUB metadata if it's an EPUB file
        if file_path.lower().endswith('.epub'):
            try:
                epub_metadata = self._extract_epub_metadata(file_path)
                metadata.update(epub_metadata)
            except Exception as e:
                logger.warning(f"Could not extract EPUB metadata from {file_path}: {e}")
        
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
                if 'isbn' in ident[1].lower() if ident[1] else False:
                    metadata['isbn'] = ident[0]
                    break
            
            return metadata
            
        except ImportError:
            logger.warning("ebooklib not available, cannot extract EPUB metadata")
            return {}
        except Exception as e:
            logger.error(f"Error extracting EPUB metadata: {e}")
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
            """Handle the 'ebook' command."""
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
        
        try:
            import beets.ui
            ebook_cmd = beets.ui.Subcommand('ebook', help='process ebook files')
            ebook_cmd.func = ebook_func
            return [ebook_cmd]
        except ImportError:
            # beets.ui not available (development mode)
            return []
