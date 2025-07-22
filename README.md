# Beets EBooks Plugin

A plugin for the [Beets](https://beets.io/) music library manager that extends its functionality to handle ebook files alongside your music collection.

## Features

- **Multi-format Support**: Handle EPUB, PDF, MOBI, AZW, AZW3, LRF, CBR, and CBZ files
- **Metadata Extraction**: Extract metadata from ebook files (especially EPUB and comic files)
- **External APIs**: Enrich metadata using Google Books API
- **Comic Book Support**: Special handling for CBR/CBZ comic files with series and issue tracking
- **Beets Integration**: Seamlessly import ebooks alongside your music using Beets' powerful library system

## Supported Formats

- **EPUB** - Full metadata extraction using ebooklib
- **PDF** - Basic metadata from filename parsing
- **MOBI/AZW/AZW3** - Amazon Kindle formats (filename parsing)
- **LRF** - Sony Reader format (filename parsing)
- **CBR/CBZ** - Comic book archives with ComicInfo.xml support

## Installation

1. Install the plugin:
```bash
pip install beets-ebooks
```

2. Enable the plugin in your Beets configuration file (`~/.config/beets/config.yaml`):
```yaml
plugins: [..., ebooks]
```

3. Configure the plugin (optional):
```yaml
ebooks:
    google_api_key: your_google_books_api_key  # Optional: for enhanced metadata
    download_covers: true
    ebook_extensions: [.epub, .pdf, .mobi, .lrf, .azw, .azw3, .cbr, .cbz]
    metadata_sources: [google_books, open_library]
    auto_import: true
```

## Usage

### Import Ebooks into Beets Library

Use the dedicated import command to add ebooks to your library:

```bash
# Import a single ebook
beet import-ebooks /path/to/book.epub

# Import all ebooks in a directory
beet import-ebooks /path/to/ebook/directory/

# Import multiple files/directories
beet import-ebooks book1.pdf book2.epub /path/to/comics/
```

### View Ebook Metadata

Display metadata for ebook files without importing:

```bash
# Show metadata for specific files
beet ebook book.epub comic.cbz

# Process multiple files
beet ebook *.epub *.cbz
```

### Query Your Ebook Library

Once imported, you can query your ebooks using standard Beets queries:

```bash
# List all ebooks
beet ls ebook:true

# Find books by author
beet ls book_author:tolkien

# Find books by title
beet ls book_title:'lord of the rings'

# Find comics by series
beet ls series:batman

# Find books by format
beet ls file_format:epub
beet ls file_format:cbz

# Complex queries
beet ls ebook:true published_year:2020..2023
```

## Comic Book Features

The plugin provides special support for comic book files:

### Filename Parsing
Comic files with naming patterns like "Batman - Detective Comics 001.cbz" are automatically parsed to extract:
- **Series**: Batman
- **Title**: Detective Comics  
- **Issue Number**: 1

### ComicInfo.xml Support
If CBR/CBZ files contain a ComicInfo.xml file, the plugin extracts:
- Title, Series, Writer, Publisher
- Issue number, page count, year
- Genre, summary, language

### Comic-Specific Fields
- `series` - Comic book series name
- `issue_number` - Issue number within the series
- `genre` - Comic genre (Action, Adventure, etc.)
- `summary` - Plot summary or description

## Database Schema

The plugin adds these fields to your Beets database:

### General Ebook Fields
- `book_author` - Author name
- `book_title` - Book title
- `isbn` - ISBN identifier
- `published_year` - Publication year
- `publisher` - Publisher name
- `page_count` - Number of pages
- `language` - Language code
- `file_format` - File format (EPUB, PDF, etc.)
- `ebook` - Boolean flag to identify ebooks

### Comic-Specific Fields
- `series` - Comic series name
- `issue_number` - Issue number
- `genre` - Genre classification
- `summary` - Plot summary

## Dependencies

### Required
- `beets >= 1.6.0` - Core music library manager
- `requests >= 2.25.0` - HTTP requests for API calls

### Optional
- `ebooklib >= 0.18` - Enhanced EPUB metadata extraction
- `rarfile >= 4.0` - CBR file support (requires unrar/7zip)

## Configuration Options

```yaml
ebooks:
    # Google Books API key for enhanced metadata
    google_api_key: ''
    
    # Download cover art (when available)
    download_covers: true
    
    # File extensions to recognize as ebooks
    ebook_extensions: [.epub, .pdf, .mobi, .lrf, .azw, .azw3, .cbr, .cbz]
    
    # External metadata sources
    metadata_sources: [google_books, open_library]
    
    # Automatically import ebooks during 'beet import'
    auto_import: true
```

## Examples

### Basic Usage
```bash
# Import some ebooks
beet import-ebooks ~/Books/

# Check what was imported
beet ls ebook:true

# Find fantasy books
beet ls genre:fantasy

# Find comics by publisher
beet ls publisher:'DC Comics'
```

### Advanced Queries
```bash
# Recent books by publication year
beet ls ebook:true published_year:2020..

# Large books
beet ls ebook:true page_count:500..

# Comics with specific issue ranges
beet ls series:batman issue_number:1..10

# Books in specific languages
beet ls language:en
```

## Development

This plugin is designed to gracefully handle missing dependencies. It will work with basic functionality even if optional libraries like `ebooklib` or `rarfile` are not installed.

For development setup:
```bash
git clone https://github.com/yourusername/beets-ebooks
cd beets-ebooks
pip install -e .
```

## Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
