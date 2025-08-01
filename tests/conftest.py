"""Test configuration for DeepL provider tests."""

import pytest
from mt_providers.types import TranslationConfig


@pytest.fixture
def deepl_config():
    """Basic test configuration for DeepL provider."""
    return TranslationConfig(
        api_key="test-deepl-key:fx",  # Free tier key format
        timeout=30
    )


@pytest.fixture
def deepl_config_pro():
    """Pro tier test configuration for DeepL provider."""
    return TranslationConfig(
        api_key="test-deepl-key",  # Pro tier key format
        timeout=30
    )


@pytest.fixture
def sample_texts():
    """Sample texts for testing."""
    return {
        "short": "Hello world",
        "long": "This is a longer text that needs translation and testing",
        "special": "Text with special chars: @#$%^&*()",
        "unicode": "🌍 Hello 世界",
        "empty": "",
        "whitespace": "   ",
    }


@pytest.fixture
def deepl_response_single():
    """Mock DeepL API response for single translation."""
    return {
        "translations": [
            {
                "detected_source_language": "EN",
                "text": "¡Hola mundo!"
            }
        ]
    }


@pytest.fixture
def deepl_response_bulk():
    """Mock DeepL API response for bulk translation."""
    return {
        "translations": [
            {
                "detected_source_language": "EN", 
                "text": "¡Hola mundo!"
            },
            {
                "detected_source_language": "EN",
                "text": "¿Cómo estás?"
            },
            {
                "detected_source_language": "EN",
                "text": "¡Adiós!"
            }
        ]
    }


@pytest.fixture
def deepl_usage_response():
    """Mock DeepL usage API response."""
    return {
        "character_count": 12345,
        "character_limit": 500000
    }
