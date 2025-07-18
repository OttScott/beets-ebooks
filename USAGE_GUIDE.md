# Beets Ebooks Collection Management Guide

## 🎉 Your Setup is Working!

Your beets-ebooks plugin is now successfully integrated with your beets installation. Here's how to use it effectively:

## ✅ What's Working

- ✅ Beets 2.3.1 installed and working
- ✅ Ebooks plugin loaded and active
- ✅ Google Books API integration working
- ✅ Metadata extraction from filenames
- ✅ EPUB metadata extraction
- ✅ PDF basic metadata extraction

## 🛠️ Available Commands

### 1. Process Individual Ebooks
```bash
beet ebook "path/to/book.epub"
beet ebook "Author - Title.pdf"
```

### 2. Batch Process Collections
Use the provided `ebook_manager.py` script:

```bash
# Analyze your collection structure
python ebook_manager.py analyze "C:/Books/"

# Analyze only EPUB files
python ebook_manager.py analyze "C:/Books/" --ext .epub

# Process all ebooks in a directory
python ebook_manager.py scan "C:/Books/"

# Process only specific file types
python ebook_manager.py scan "C:/Books/" --ext .epub,.pdf

# Process a single file
python ebook_manager.py process "book.epub"

# Import ebooks to beets library with filtering
python ebook_manager.py import "C:/Books/" --ext .epub
python ebook_manager.py batch-import "C:/Books/" --ext .epub,.mobi
```

#### File Type Filtering

You can filter by specific ebook formats using the `--ext` option:

- **Single format:** `--ext .epub`
- **Multiple formats:** `--ext .epub,.pdf,.mobi`
- **Case insensitive:** `--ext .EPUB,.PDF` (automatically normalized)
- **Without dots:** `--ext epub,pdf` (dots added automatically)

**Supported formats:** `.epub`, `.pdf`, `.mobi`, `.lrf`, `.azw`, `.azw3`

## 📁 Your Current Configuration

**Beets Config Location:** `F:\ottsc\AppData\Roaming\beets\config.yaml`

**Key Settings:**
- **Library:** `F:\ottsc\AppData\Roaming\beets\library.db`
- **Sorted Books Directory:** `B:\Books\Beets\SortedBooks`
- **Plugin Path:** `F:\ottsc\AppData\Roaming\beets\beetsplug`
- **Google API Key:** Configured and working ✅

**Path Pattern:** `$book_author/$series/$book_title`

## 🚀 Recommended Workflow

### 1. **Scan Your Existing Collection**
```bash
cd "F:\src\Workspaces\Beets-ebooks"
python ebook_manager.py analyze "C:/Your/Ebook/Directory"
```

### 2. **Process and Enrich Metadata**
```bash
python ebook_manager.py scan "C:/Your/Ebook/Directory"
```

### 3. **Organize by Author Structure**
Based on the path pattern in your config (`$book_author/$series/$book_title`), organize your ebooks like:
```
B:\Books\Beets\SortedBooks\
├── J.R.R. Tolkien\
│   ├── The Lord of the Rings\
│   └── The Hobbit\
├── Agatha Christie\
│   ├── Murder on the Orient Express\
│   └── The Murder of Roger Ackroyd\
└── ...
```

## 🔧 Advanced Usage

### Custom Metadata Sources
Your plugin supports multiple metadata sources. You can modify the config:
```yaml
ebooks:
  metadata_sources: ['google_books', 'open_library']
  google_api_key: "your_key_here"
```

### Supported File Formats
- **EPUB** (.epub) - Full metadata extraction
- **PDF** (.pdf) - Basic metadata + filename parsing
- **MOBI** (.mobi) - Filename parsing
- **LRF** (.lrf) - Filename parsing
- **AZW/AZW3** (.azw, .azw3) - Filename parsing

### Filename Convention
For best results, name your files as:
- `Author Name - Book Title.ext`
- `J.R.R. Tolkien - The Lord of the Rings.epub`
- `Agatha Christie - Murder on the Orient Express.pdf`

## 🐛 Troubleshooting

### If beets command not found:
```bash
# Use full path
"F:\ottsc\AppData\Roaming\Python\Python313\Scripts\beet.exe" ebook "book.epub"
```

### Check Plugin Status:
```bash
beet version  # Should show "plugins: ebooks"
```

### Check Configuration:
```bash
beet config  # Shows current configuration
```

## 📊 Example Output

When you process an ebook, you'll see:
```
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

## 🔄 Next Steps

1. **Scan your existing ebook collection** using the analyzer
2. **Process files** to enrich metadata
3. **Organize** your library according to the established pattern
4. **Consider** creating automated scripts for regular processing

## 💡 Tips

- **API Rate Limits:** The Google Books API has rate limits. For large collections, consider adding delays between requests.
- **Backup:** Always backup your files before reorganizing.
- **File Naming:** Consistent naming helps with automatic metadata extraction.
- **Series Support:** The path pattern includes `$series` - you can extend the plugin to support series detection.

Your beets-ebooks plugin is ready to help you organize and manage your ebook collection! 🎉
