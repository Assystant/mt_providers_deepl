# Changelog

All notable changes to the DeepL Translator Provider will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive API documentation in README
- Contributing guidelines (CONTRIBUTING.md)
- Detailed troubleshooting guide
- Integration examples for web frameworks (Flask, FastAPI)
- Usage monitoring and quota management examples
- Language support documentation
- Development environment setup guide

### Changed
- Enhanced README with complete feature overview
- Improved error handling documentation
- Extended configuration options documentation
- Updated usage examples with more scenarios

### Fixed
- Documentation formatting and structure improvements

## [0.1.1] - 2025-08-01

### Added
- Initial release of DeepL Translator Provider
- Full sync and async translation support with `translate()`, `bulk_translate()`, `translate_async()`, and `bulk_translate_async()` methods
- Official DeepL Python SDK integration for optimal performance
- Automatic detection of free vs pro API tiers
- Language auto-detection support
- Usage monitoring with `get_usage_info()` method
- Supported languages discovery with `get_supported_languages()` method
- Comprehensive error handling with DeepL-specific exceptions
- Type annotations and mypy support
- Character limit validation (30,000 characters per request)
- Batch translation with empty text handling
- Comprehensive test suite with async coverage
- CI/CD workflows for multiple Python versions

### Changed
- Uses mt_providers framework version >=0.1.7
- Optimized batch translation performance with proper text mapping
- Enhanced error messages with more context

### Fixed
- Entry point configuration for provider discovery
- Import structure and module exports
- Language code mapping to DeepL format
- Empty text handling in batch operations
- Async session management

---

## Guidelines for Changelog Entries

### Types of Changes

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

### Format

Each entry should:
- Use present tense ("Add feature" not "Added feature")
- Be concise but descriptive
- Include breaking changes in the **Changed** section with clear migration notes
- Reference issue numbers when applicable: "Fix timeout handling (#42)"

### Version Format

Versions follow SemVer format: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Process

1. Update version number in `pyproject.toml` and `__init__.py`
2. Move **Unreleased** items to new version section
3. Add release date
4. Create new **Unreleased** section
5. Commit changes
6. Create git tag: `git tag -a v0.1.1 -m "Release v0.1.1"`
7. Push with tags: `git push origin main --tags`
8. Publish to PyPI: `python -m build && python -m twine upload dist/*`
