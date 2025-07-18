# Beets Ebooks Plugin

A [Beets](https://beets.io/) plugin for managing ebook collections alongside your music library.

## Features

- **Ebook Detection**: Automatically discovers ebook files (EPUB, PDF, MOBI, LRF, AZW, AZW3) during import
- **Metadata Extraction**: Extracts metadata from ebook files, with special support for EPUB format
- **External Metadata Sources**: Enriches metadata using Google Books API and other sources
- **Seamless Integration**: Works with existing Beets workflows and commands
- **Custom Fields**: Adds ebook-specific fields like author, ISBN, publisher, page count, etc.
- **File Type Filtering**: Import only specific ebook formats using the `--ext` option

## Installation

### From Source (Development)

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/beets-ebooks.git
   cd beets-ebooks
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

3. Enable the plugin in your Beets configuration file (`~/.config/beets/config.yaml`):
   ```yaml
   plugins: ebooks
   
   ebooks:
     google_api_key: your_api_key_here  # Optional
     download_covers: true
     ebook_extensions: ['.epub', '.pdf', '.mobi', '.lrf', '.azw', '.azw3']
     metadata_sources: ['google_books', 'open_library']
   ```

### From PyPI (When Available)

```bash
pip install beets-ebooks
```

## Configuration

Add the following to your Beets configuration:

```yaml
plugins: ebooks

ebooks:
  # Google Books API key for enhanced metadata (optional)
  google_api_key: ''
  
  # Whether to download cover art
  download_covers: true
  
  # File extensions to treat as ebooks
  ebook_extensions: ['.epub', '.pdf', '.mobi', '.lrf', '.azw', '.azw3']
  
  # External metadata sources to use
  metadata_sources: ['google_books', 'open_library']
```

### Google Books API Setup

To get enhanced metadata from Google Books:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Books API
4. Create credentials (API key)
5. Add the API key to your Beets configuration

## Usage

### Process Individual Ebooks

The primary way to use this plugin is with the `ebook` command to process specific ebook files:

```bash
beet ebook /path/to/book.epub
beet ebook /path/to/ebooks/
```

This will extract and display metadata for the specified ebook(s), including:
- Basic metadata from filename parsing
- EPUB metadata extraction (for .epub files)
- Enhanced metadata from Google Books API

### Example Output

```bash
$ beet ebook "J.R.R. Tolkien - The Lord of the Rings.epub"
Processing ebook: J.R.R. Tolkien - The Lord of the Rings.epub
Extracted metadata:
  file_format: EPUB
  path: /path/to/book.epub
  book_author: J.R.R. Tolkien
  book_title: The Lord of the Rings
Fetching external metadata...
External metadata:
  published_year: 2001
  publisher: Mariner Books
  page_count: 1176
  language: en
```

### Batch Processing

Process all ebooks in a directory:

```bash
beet ebook /path/to/ebook/collection/
```

### Integration with Beets Import

Currently, this plugin works alongside beets but doesn't integrate directly with the `beet import` command, as beets is primarily designed for music files. The plugin provides a separate `ebook` command for ebook management.

### File Type Filtering

To import only specific ebook formats, use the `--ext` option with the `beet ebook` command:

```bash
beet ebook --ext epub,mobi /path/to/ebooks/
```

This will process only the files with the specified extensions.

## Ebook Fields

The plugin adds the following fields to your Beets library:

- `book_author`: The book's author(s)
- `book_title`: The book's title
- `isbn`: ISBN number
- `published_year`: Year of publication
- `publisher`: Publisher name
- `page_count`: Number of pages
- `language`: Language code (e.g., 'en', 'fr')
- `file_format`: File format (EPUB, PDF, etc.)

## Supported File Formats

- **EPUB** (.epub) - Full metadata extraction supported
- **PDF** (.pdf) - Basic metadata extraction
- **MOBI** (.mobi) - Basic filename parsing
- **LRF** (.lrf) - Basic filename parsing  
- **AZW/AZW3** (.azw, .azw3) - Basic filename parsing

## Development

### Setting Up Development Environment

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. Run tests:
   ```bash
   python -m pytest tests/
   ```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Dependencies

- **beets** >= 1.6.0 - The music library manager this plugin extends
- **requests** >= 2.25.0 - For making API calls to metadata sources
- **ebooklib** >= 0.18 - For EPUB metadata extraction
- **PyPDF2** >= 3.0.0 - For PDF metadata extraction

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Beets](https://beets.io/) - The excellent music library manager that inspired this plugin
- [Google Books API](https://developers.google.com/books) - For providing book metadata
- The open-source community for the various ebook processing libraries
