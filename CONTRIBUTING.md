# Contributing to DeepL Translator Provider

Thank you for your interest in contributing to the DeepL Translator Provider! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Code Style](#code-style)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- DeepL API key (for integration testing)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/mt_providers_deepl.git
   cd mt_providers_deepl
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e ".[test,docs,dev]"
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Verify Setup**
   ```bash
   pytest
   ```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix issues in the codebase
- **Features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Performance**: Optimize existing code
- **Refactoring**: Improve code structure without changing functionality

### Before You Start

1. **Check existing issues**: Look for existing issues or discussions about your planned contribution
2. **Create an issue**: If no issue exists, create one to discuss your proposal
3. **Get feedback**: Wait for maintainer feedback before starting significant work

### Branch Naming

Use descriptive branch names:
- `feature/add-document-translation`
- `bugfix/fix-language-detection`
- `docs/update-api-reference`
- `test/add-usage-monitoring-tests`

## Pull Request Process

### 1. Preparation

- Ensure your fork is up to date with the main repository
- Create a feature branch from `main`
- Make your changes in logical, atomic commits

### 2. Implementation

- Write clear, concise commit messages
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Submission

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Use the provided PR template
   - Provide clear description of changes
   - Reference related issues
   - Add appropriate labels

3. **Address Feedback**
   - Respond to review comments
   - Make requested changes
   - Keep PR up to date with main branch

### Pull Request Template

```markdown
## Description

Brief description of the changes and their purpose.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally
- [ ] Manual testing completed

## DeepL API Testing

- [ ] Tested with free tier API key
- [ ] Tested with pro tier API key (if applicable)
- [ ] Usage monitoring verified
- [ ] Language detection tested

## Checklist

- [ ] Code follows the project's style guidelines
- [ ] Self-review of code completed
- [ ] Documentation updated (if applicable)
- [ ] Tests added for new functionality
- [ ] All checks pass

## Additional Notes

Any additional information, dependencies, or context.
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mt_provider_deepl --cov-report=html

# Run specific test categories
pytest tests/test_translator.py -v
pytest -k "async" -v
pytest -k "not integration" -v
```

### Writing Tests

#### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from mt_provider_deepl import DeepLTranslator

def test_translate_success():
    """Test successful translation."""
    config = Mock()
    translator = DeepLTranslator(config)
    
    with patch.object(translator.client, 'translate_text') as mock_translate:
        mock_result = Mock()
        mock_result.text = 'Hallo Welt'
        mock_result.detected_source_lang = 'EN'
        mock_translate.return_value = mock_result
        
        result = translator.translate("Hello world", "en", "de")
        
        assert result['translated_text'] == 'Hallo Welt'
        assert result['status'] == 'success'
        mock_translate.assert_called_once()
```

#### Integration Tests

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_translation():
    """Test real translation with DeepL API."""
    config = TranslationConfig(
        api_key=os.getenv("DEEPL_API_KEY")
    )
    
    if not config.api_key:
        pytest.skip("DeepL API key not available")
    
    translator = DeepLTranslator(config)
    result = await translator.translate_async("Hello", "en", "de")
    
    assert result['status'] == 'success'
    assert len(result['translated_text']) > 0
```

#### Test Categories

Use pytest markers to categorize tests:

```python
@pytest.mark.unit          # Unit tests (fast, no external dependencies)
@pytest.mark.integration   # Integration tests (require API keys)
@pytest.mark.async         # Async-specific tests
@pytest.mark.slow          # Slow tests (e.g., large batch processing)
@pytest.mark.usage         # Usage monitoring tests
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Import formatting**: Use isort
- **Type hints**: Required for all public APIs
- **Docstrings**: Google style

### Tools

#### Black (Code Formatting)
```bash
black mt_provider_deepl/ tests/
```

#### isort (Import Sorting)
```bash
isort mt_provider_deepl/ tests/
```

#### flake8 (Linting)
```bash
flake8 mt_provider_deepl/ tests/
```

#### mypy (Type Checking)
```bash
mypy mt_provider_deepl/
```

### Pre-commit Configuration

The project uses pre-commit hooks to ensure code quality:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
```

### Code Organization

```
mt_provider_deepl/
├── __init__.py           # Package initialization
├── translator.py         # Main translator implementation
├── exceptions.py         # Custom exceptions (if needed)
└── utils.py             # Utility functions (if needed)

tests/
├── __init__.py
├── conftest.py          # Pytest configuration
├── test_translator.py   # Main translator tests
├── test_async.py        # Async-specific tests
├── test_usage.py        # Usage monitoring tests
└── integration/         # Integration tests
    └── test_real_api.py
```

## Documentation

### Docstring Style

Use Google-style docstrings:

```python
def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
    """Translate text from source language to target language.
    
    Args:
        text: The text to translate (max 30,000 characters).
        source_lang: Source language code (ISO 639-1) or "auto".
        target_lang: Target language code (ISO 639-1).
        
    Returns:
        Translation result with translated text and metadata.
        
    Raises:
        TranslationError: If translation fails.
        ConfigurationError: If configuration is invalid.
        
    Example:
        >>> translator = DeepLTranslator(config)
        >>> result = translator.translate("Hello", "en", "de")
        >>> print(result['translated_text'])
        'Hallo'
    """
```

### README Updates

When adding features, update the README:

1. Add new features to the features list
2. Update usage examples
3. Add new configuration options
4. Update API reference section

### Changelog

Update `CHANGELOG.md` for all changes:

```markdown
## [Unreleased]

### Added
- New feature description

### Changed
- Changed feature description

### Fixed
- Bug fix description

### Deprecated
- Deprecated feature description

### Removed
- Removed feature description
```

## DeepL-Specific Guidelines

### API Usage

When working with DeepL API:

1. **Always test with both free and pro tier keys**
2. **Monitor usage to avoid quota exceeded errors**
3. **Handle language variants correctly (e.g., EN-US vs EN-GB)**
4. **Test with various text sizes up to the 30k character limit**

### Language Handling

```python
# Good: Handle DeepL language variants
def _map_language_code(self, lang_code: str) -> str:
    language_map = {
        "en": "EN-US",  # Default to US English
        "pt": "PT-PT",  # Default to European Portuguese
    }
    return language_map.get(lang_code.lower(), lang_code.upper())

# Good: Test language detection
def test_language_detection(self):
    result = translator.translate("Bonjour", "auto", "en")
    assert result['metadata']['detected_language'] == 'fr'
```

### Usage Monitoring

```python
# Good: Include usage monitoring in tests
def test_usage_monitoring(self):
    usage = translator.get_usage_info()
    assert 'character_count' in usage
    assert 'character_limit' in usage
```

## Release Process

### Version Numbering

We use Semantic Versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `pyproject.toml` and `__init__.py`
2. Update `CHANGELOG.md`
3. Ensure all tests pass
4. Update documentation
5. Create release PR
6. Tag release after merge
7. Publish to PyPI

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Request Reviews**: Code-specific discussions

### Maintainer Response Time

- **Issues**: We aim to respond within 48 hours
- **Pull Requests**: We aim to provide initial feedback within 72 hours
- **Security Issues**: We aim to respond within 24 hours

### Contact

For sensitive issues or private communication, contact the maintainers directly.

---

Thank you for contributing to the DeepL Translator Provider! Your contributions help make this project better for everyone.
