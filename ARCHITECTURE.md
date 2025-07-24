# Architecture Migration

This document explains the refactoring of the beets-ebooks project to separate concerns between the core plugin and utility tools.

## Before: Monolithic Structure

Previously, this repository contained:
- Beets plugin (`beetsplug/ebooks.py`)
- Standalone CLI utility (`ebook_manager.py`)
- Advanced features (--onefile, extension filtering)
- Mixed test suites

## After: Clean Separation

### This Repository (beets-ebooks)
**Focus**: Pure Beets plugin

**Contains**:
- `beetsplug/ebooks.py` - Core plugin implementation
- Plugin-specific tests (`tests/test_ebooks.py`)
- Beets integration and configuration
- Plugin entry points

**Responsibilities**:
- Ebook file detection during Beets import
- Metadata extraction and enrichment
- Custom field definitions
- Integration with Beets commands and workflows

### Companion Repository (ebook-manager)
**Focus**: Standalone ebook management utility

**Contains**:
- `ebook_manager.py` - CLI utility with advanced features
- `--onefile` functionality for format deduplication
- Extension filtering (`--ext`)
- Batch operations and collection analysis
- Comprehensive test suite for utility functions

**Responsibilities**:
- Advanced ebook collection management
- Format filtering and deduplication
- Batch import operations
- Collection analysis and organization suggestions

## Interoperability

The two components work together through:

1. **Shared Commands**: ebook-manager calls beets commands provided by this plugin
2. **Clean Interfaces**: Plugin provides stable beets commands that utilities can use
3. **Optional Integration**: ebook-manager can optionally depend on beets-ebooks
4. **Independent Installation**: Each can be installed and used separately

## Benefits

1. **Focused Repositories**: Each repo has a clear, single purpose
2. **Easier Maintenance**: Simpler codebases with fewer dependencies
3. **Flexible Installation**: Users can install just what they need
4. **Better Testing**: Targeted test suites for each component
5. **Cleaner APIs**: Well-defined interfaces between components

## Migration Path

For existing users:

1. **Plugin Users**: No changes needed - plugin functionality remains the same
2. **CLI Utility Users**: Install the new ebook-manager package for advanced features
3. **Combined Users**: Install both packages for full functionality

The plugin API remains stable, ensuring backward compatibility.
