# --onefile Feature Implementation

## Overview

The `--onefile` feature has been successfully implemented for the Beets Ebooks plugin. This feature allows users to import only one file per book when multiple formats exist, automatically selecting the highest priority format.

## Feature Details

### Priority Order
The system uses the following priority order (highest to lowest):
1. `.epub` (Priority 6) - Highest priority, widely supported
2. `.mobi` (Priority 5) - Amazon Kindle format  
3. `.azw` (Priority 4) - Amazon Kindle format
4. `.azw3` (Priority 3) - Amazon Kindle format
5. `.pdf` (Priority 2) - Portable Document Format
6. `.lrf` (Priority 1) - Lowest priority, Sony format

### How It Works
1. **Book Identification**: Groups files by extracting "Author - Title" patterns from filenames
2. **Format Selection**: For each book group, selects the format with the highest priority
3. **Duplicate Handling**: Automatically skips lower-priority duplicates
4. **Filtering Integration**: Works seamlessly with `--ext` filtering

### Usage Examples

#### Basic Usage
```bash
# Import only the best format per book
python ebook_manager.py import /path/to/books --onefile

# Scan and see what would be selected
python ebook_manager.py scan /path/to/books --onefile

# Analyze collection with one-file filtering
python ebook_manager.py analyze /path/to/books --onefile
```

#### Combined with Extension Filtering
```bash
# Filter to epub/mobi only, then select best format per book
python ebook_manager.py import /path/to/books --ext .epub,.mobi --onefile

# Batch import with extension and onefile filtering
python ebook_manager.py batch-import /path/to/books --ext .epub --onefile
```

### Demonstration Output

Example with duplicate books:
```
Found 9 total ebook(s) before filtering
Book: douglas adams - the hitchhiker's guide to the galaxy
  Selected: Douglas Adams - The Hitchhiker's Guide to the Galaxy.epub
  Skipped:  Douglas Adams - The Hitchhiker's Guide to the Galaxy.mobi
  Skipped:  Douglas Adams - The Hitchhiker's Guide to the Galaxy.pdf
Book: j.r.r. tolkien - the lord of the rings
  Selected: J.R.R. Tolkien - The Lord of the Rings.epub
  Skipped:  J.R.R. Tolkien - The Lord of the Rings.mobi
  Skipped:  J.R.R. Tolkien - The Lord of the Rings.pdf
After one-file filtering: 5 ebook(s)
```

## Implementation Details

### Files Modified
- `ebook_manager.py`: Added core functionality and CLI support
- `tests/test_ebook_manager.py`: Added comprehensive tests
- `examples/onefile_demo.py`: Created feature demonstration

### New Functions Added
- `extract_book_identifier()`: Extracts book identifiers for grouping
- `filter_onefile_per_book()`: Performs the core filtering logic
- Updated all import/scan functions to support the `onefile` parameter

### Configuration
- `FORMAT_PRIORITY`: Dictionary defining format priority scores
- CLI argument: `--onefile` flag with descriptive help text

## Testing

The feature includes comprehensive test coverage:
- Book identifier extraction tests
- Format priority validation tests  
- One-file filtering logic tests
- CLI integration tests
- Combination with extension filtering tests

All 33 tests pass successfully.

## Benefits

1. **Clean Imports**: Eliminates duplicate formats automatically
2. **Smart Selection**: Chooses the most compatible/preferred format
3. **Flexible**: Works with any combination of existing filters
4. **User-Friendly**: Clear feedback on what gets selected/skipped
5. **Efficient**: Reduces library bloat and organization overhead

## Future Enhancements

Potential improvements could include:
- Custom priority order configuration
- Different book identification strategies
- Integration with the Beets plugin for automatic onefile imports
- Support for user-defined format preferences per author/series

This feature makes the Beets Ebooks plugin significantly more useful for users with large, mixed-format collections.
