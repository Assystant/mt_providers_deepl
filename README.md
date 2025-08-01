# DeepL Translator Provider

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](tests/)
[![Version](https://img.shields.io/badge/version-0.1.1-blue)](pyproject.toml)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

DeepL API integration for the [MT Providers](https://github.com/assystant/mt-providers) framework.

## Overview

This provider enables seamless integration with DeepL translation services through the MT Providers framework. It leverages the official DeepL Python SDK for robust translation capabilities with both synchronous and asynchronous operations.

## Table of Contents

- [Installation](#installation)
- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Error Handling](#error-handling)
- [Limits and Quotas](#limits-and-quotas)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.8 or higher
- DeepL API key (free or pro)

### Install from PyPI

```bash
pip install mt_provider_deepl
```

### Install for Development

```bash
git clone https://github.com/assystant/mt_providers_deepl.git
cd mt_providers_deepl
pip install -e ".[test,docs]"
```

## Features

- ✅ **Single and Batch Translations**: Translate individual texts or process multiple texts efficiently
- ✅ **Async Support**: Full async/await support with aiohttp for non-blocking operations
- ✅ **DeepL SDK Integration**: Uses official DeepL Python SDK for optimal performance
- ✅ **Free & Pro API Support**: Automatic detection and configuration for both API tiers
- ✅ **Language Detection**: Automatic source language detection when not specified
- ✅ **Usage Monitoring**: Built-in usage tracking and quota monitoring
- ✅ **Error Handling**: Comprehensive error handling with detailed error messages
- ✅ **Type Safety**: Full type annotations with mypy support
- ✅ **Framework Integration**: Seamless integration with MT Providers ecosystem

## Configuration

### Basic Configuration

```python
from mt_providers.types import TranslationConfig

# Free API configuration
config = TranslationConfig(
    api_key="your-deepl-api-key:fx",  # Free tier API key ends with :fx
    timeout=30
)

# Pro API configuration
config = TranslationConfig(
    api_key="your-deepl-pro-api-key",  # Pro tier API key
    timeout=30
)
```

### Environment Variables

```python
import os
from mt_providers.types import TranslationConfig

config = TranslationConfig(
    api_key=os.getenv("DEEPL_API_KEY"),
    timeout=int(os.getenv("DEEPL_TIMEOUT", "30"))
)
```

### Configuration Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `api_key` | str | Yes | - | DeepL API key (free or pro) |
| `endpoint` | str | No | Auto-detected | Custom API endpoint URL |
| `timeout` | int | No | 30 | Request timeout in seconds |

## Usage Examples

### Basic Translation

```python
from mt_providers import get_provider
from mt_providers.types import TranslationConfig

# Configure the provider
config = TranslationConfig(
    api_key="your-deepl-api-key:fx"
)

# Get the DeepL provider
translator = get_provider("deepl")(config)

# Translate a single text
result = translator.translate("Hello world", "en", "de")
print(f"Translation: {result['translated_text']}")  # "Hallo Welt"
print(f"Detected language: {result['metadata']['detected_language']}")
```

### Batch Translation

```python
# Translate multiple texts efficiently
texts = [
    "Hello world",
    "How are you?", 
    "Good morning",
    "Thank you very much"
]

results = translator.bulk_translate(texts, "en", "de")

for i, result in enumerate(results):
    print(f"{texts[i]} → {result['translated_text']}")
    # Hello world → Hallo Welt
    # How are you? → Wie geht es Ihnen?
    # Good morning → Guten Morgen
    # Thank you very much → Vielen Dank
```

### Async Translation

```python
import asyncio

async def async_translate_example():
    # Single async translation
    result = await translator.translate_async("Hello world", "en", "fr")
    print(f"Async result: {result['translated_text']}")  # "Bonjour le monde"
    
    # Batch async translation
    texts = ["Hello", "World", "Python"]
    results = await translator.bulk_translate_async(texts, "en", "es")
    
    for text, result in zip(texts, results):
        print(f"{text} → {result['translated_text']}")

# Run async function
asyncio.run(async_translate_example())
```

### Language Auto-Detection

```python
# Let DeepL detect the source language
result = translator.translate("Bonjour le monde", "auto", "en")
print(f"Translation: {result['translated_text']}")  # "Hello world"
print(f"Detected: {result['metadata']['detected_language']}")  # "fr"
```

### Error Handling

```python
from mt_providers.exceptions import (
    ConfigurationError,
    TranslationError, 
    ProviderError
)
from mt_providers.types import TranslationStatus

try:
    result = translator.translate("Hello", "en", "de")
    
    if result['status'] == TranslationStatus.SUCCESS:
        print(f"Success: {result['translated_text']}")
    else:
        print(f"Translation failed: {result['error']}")
        
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except TranslationError as e:
    print(f"Translation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## API Reference

### DeepLTranslator Class

The main translator class that implements the MT Providers interface.

#### Methods

##### `translate(text: str, source_lang: str, target_lang: str) -> TranslationResult`

Translates a single text synchronously.

**Parameters:**
- `text` (str): Text to translate (max 30,000 characters)
- `source_lang` (str): Source language code (ISO 639-1, e.g., "en", "de") or "auto"
- `target_lang` (str): Target language code (ISO 639-1, e.g., "fr", "es")

**Returns:**
- `TranslationResult`: Dictionary with translation results and metadata

**Example:**
```python
result = translator.translate("Hello", "en", "de")
# Returns: {
#     'translated_text': 'Hallo',
#     'status': TranslationStatus.SUCCESS,
#     'metadata': {
#         'detected_language': 'en',
#         'confidence': 1.0,
#         'provider': 'deepl',
#         'model': 'deepl-api',
#         'billed_characters': 5
#     }
# }
```

##### `bulk_translate(texts: List[str], source_lang: str, target_lang: str) -> List[TranslationResult]`

Translates multiple texts in a single batch request.

##### `translate_async(text: str, source_lang: str, target_lang: str) -> TranslationResult`

Asynchronous version of `translate()`.

##### `bulk_translate_async(texts: List[str], source_lang: str, target_lang: str) -> List[TranslationResult]`

Asynchronous version of `bulk_translate()`.

##### `get_supported_languages() -> Dict[str, List[str]]`

Get supported source and target languages from DeepL API.

**Returns:**
```python
{
    "source": ["en", "de", "fr", "es", ...],
    "target": ["en-us", "en-gb", "de", "fr", ...]
}
```

##### `get_usage_info() -> Dict[str, Any]`

Get current usage information and quotas.

**Returns:**
```python
{
    "character_count": 12500,
    "character_limit": 500000,
    "character_limit_reached": False,
    "document_count": 0,
    "document_limit": 0
}
```

### Supported Languages

DeepL supports 30+ languages with high quality. Common language codes include:

| Language | Code | Language | Code |
|----------|------|----------|------|
| English (US) | en-us | German | de |
| English (UK) | en-gb | French | fr |
| Spanish | es | Italian | it |
| Portuguese (EU) | pt-pt | Portuguese (BR) | pt-br |
| Russian | ru | Japanese | ja |
| Chinese | zh | Polish | pl |
| Dutch | nl | Swedish | sv |

For the complete list, call `translator.get_supported_languages()`.

## Error Handling

### Exception Types

The provider raises specific exceptions for different error scenarios:

```python
from mt_providers.exceptions import (
    ConfigurationError,     # Invalid configuration
    TranslationError,       # Translation-specific errors
    ProviderError,          # Provider-specific errors
    RateLimitError,         # Rate limit exceeded
    TimeoutError           # Request timeout
)
```

### DeepL-Specific Errors

```python
import deepl

try:
    result = translator.translate("Hello", "en", "invalid-lang")
except deepl.AuthorizationException:
    print("Invalid API key")
except deepl.QuotaExceededException:
    print("Translation quota exceeded")
except deepl.TooManyRequestsException:
    print("Too many requests")
except deepl.DeepLException as e:
    print(f"DeepL API error: {e}")
```

### Status Codes

Translation results include status information:

```python
from mt_providers.types import TranslationStatus

result = translator.translate("Hello", "en", "de")

if result['status'] == TranslationStatus.SUCCESS:
    print("Translation successful")
elif result['status'] == TranslationStatus.ERROR:
    print(f"Translation failed: {result['error']}")
```

## Limits and Quotas

### DeepL API Limits

- **Character limit**: 30,000 characters per request
- **Free tier**: 500,000 characters/month
- **Pro tier**: Based on subscription plan
- **Rate limits**: No specific rate limits, but usage monitoring available

### Usage Monitoring

```python
# Check current usage
usage = translator.get_usage_info()
print(f"Used: {usage['character_count']}/{usage['character_limit']} characters")
print(f"Remaining: {usage['character_limit'] - usage['character_count']} characters")

if usage['character_limit_reached']:
    print("⚠️ Character limit reached!")
```

### Best Practices

```python
# Monitor usage before large operations
usage = translator.get_usage_info()
remaining = usage['character_limit'] - usage['character_count']

if remaining < len(text_to_translate):
    print("Not enough quota remaining")
else:
    result = translator.translate(text_to_translate, "en", "de")
```

## Troubleshooting

### Common Issues

#### 1. API Key Problems

```python
# Free tier API key format
api_key = "your-key:fx"  # Must end with :fx

# Pro tier API key format  
api_key = "your-key"     # No :fx suffix
```

#### 2. Language Code Issues

```python
# DeepL uses specific language variants
result = translator.translate("Hello", "en", "en-us")  # ✓ Valid
result = translator.translate("Hello", "en", "en")     # ✗ Use specific variant
```

#### 3. Quota Management

```python
# Check quota before translation
usage = translator.get_usage_info()
if usage['character_limit_reached']:
    print("Quota exceeded - upgrade plan or wait for reset")
```

## Integration Examples

### Web Application Integration

```python
from flask import Flask, request, jsonify
from mt_providers import get_provider
from mt_providers.types import TranslationConfig

app = Flask(__name__)

# Initialize translator
config = TranslationConfig(
    api_key=os.getenv("DEEPL_API_KEY")
)
translator = get_provider("deepl")(config)

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json
    
    try:
        result = translator.translate(
            data['text'],
            data.get('source_lang', 'auto'),
            data['target_lang']
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/usage', methods=['GET'])
def get_usage():
    """Get current API usage information."""
    try:
        usage = translator.get_usage_info()
        return jsonify(usage)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
```

### Async FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mt_providers import get_provider
from mt_providers.types import TranslationConfig

app = FastAPI()

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str

# Initialize async translator
config = TranslationConfig(
    api_key=os.getenv("DEEPL_API_KEY")
)
translator = get_provider("deepl")(config)

@app.post("/translate")
async def translate_text(request: TranslationRequest):
    try:
        result = await translator.translate_async(
            request.text,
            request.source_lang,
            request.target_lang
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/languages")
async def get_languages():
    """Get supported languages."""
    try:
        languages = translator.get_supported_languages()
        return languages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/assystant/mt_providers_deepl.git
cd mt_providers_deepl

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[test,docs,dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mt_provider_deepl --cov-report=html

# Run only async tests
pytest -k "async"

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black mt_provider_deepl/ tests/

# Sort imports
isort mt_provider_deepl/ tests/

# Lint code
flake8 mt_provider_deepl/ tests/

# Type checking
mypy mt_provider_deepl/
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `pytest`
5. Ensure code quality: `black . && isort . && flake8`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [MT Providers Documentation](https://mt-providers.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/assystant/mt_providers_deepl/issues)
- **DeepL API**: [DeepL API Documentation](https://www.deepl.com/docs-api)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

---

**Made with ❤️ by the MT Providers team**
