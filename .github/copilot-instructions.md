<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Beets Ebooks Plugin Development

This is a Python plugin for the Beets music library manager that extends its functionality to handle ebook files.

## Project Structure
- `beetsplug/ebooks.py` - Main plugin implementation
- `setup.py` - Package setup and dependencies  
- `pyproject.toml` - Modern Python packaging configuration
- `requirements.txt` - Development dependencies

## Key Concepts
- **Beets Plugin Architecture**: This plugin extends BeetsPlugin and integrates with Beets' import system
- **Metadata Extraction**: Extract metadata from ebook files (especially EPUB) using ebooklib
- **External APIs**: Enrich metadata using Google Books API and other sources
- **Custom Fields**: Add ebook-specific database fields to Beets library

## Development Guidelines
- Follow Beets plugin conventions and patterns
- Handle missing dependencies gracefully (beets, ebooklib, requests may not be installed during development)
- Use proper logging via the beets logging system
- Implement proper error handling for file operations and API calls
- Support multiple ebook formats with extensible architecture

## Testing Considerations
- Test with various ebook formats (EPUB, PDF, MOBI, etc.)
- Mock external API calls in tests
- Test both successful and error scenarios
- Verify integration with Beets import workflows

## Dependencies
- `beets >= 1.6.0` - Core music library manager
- `requests >= 2.25.0` - HTTP requests for API calls
- `ebooklib >= 0.18` - EPUB file handling
- `PyPDF2 >= 3.0.0` - PDF metadata extraction
