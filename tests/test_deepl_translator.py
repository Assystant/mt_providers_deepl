"""Comprehensive tests for DeepL translator provider."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from mt_providers.types import TranslationConfig, TranslationStatus
from mt_providers.exceptions import ConfigurationError, TranslationError
from mt_provider_deepl.translator import DeepLTranslator


class TestDeepLTranslatorInit:
    """Test DeepL translator initialization and configuration."""

    def test_init_with_valid_config(self, deepl_config):
        """Test initialization with valid configuration."""
        translator = DeepLTranslator(deepl_config)
        
        assert translator.config == deepl_config
        assert translator.name == "deepl"
        assert translator.supports_async is True
        assert translator.min_supported_version == "0.1.8"
        assert translator.max_chunk_size == 30000
        assert translator.requires_region is False

    def test_init_missing_api_key(self):
        """Test initialization with missing API key."""
        config = TranslationConfig(api_key="")
        translator = DeepLTranslator(config)
        
        with pytest.raises(ConfigurationError, match="API key is required"):
            translator.translate("test", "en", "es")

    def test_free_api_key_detection(self, deepl_config):
        """Test detection of free tier API key."""
        translator = DeepLTranslator(deepl_config)
        assert translator.is_free_api is True
        assert translator.base_url == "https://api-free.deepl.com"

    def test_pro_api_key_detection(self, deepl_config_pro):
        """Test detection of pro tier API key."""
        translator = DeepLTranslator(deepl_config_pro)
        assert translator.is_free_api is False
        assert translator.base_url == "https://api.deepl.com"


class TestLanguageMapping:
    """Test language code mapping functionality."""

    def test_language_mapping(self, deepl_config):
        """Test language code mapping to DeepL format."""
        translator = DeepLTranslator(deepl_config)
        
        # Test specific mappings
        assert translator._map_language_code("en") == "EN-US"
        assert translator._map_language_code("pt") == "PT-PT"
        assert translator._map_language_code("zh") == "ZH"
        
        # Test uppercase conversion
        assert translator._map_language_code("de") == "DE"
        assert translator._map_language_code("fr") == "FR"
        assert translator._map_language_code("es") == "ES"


class TestSyncTranslation:
    """Test synchronous translation methods."""

    @patch('deepl.Translator')
    def test_translate_success(self, mock_deepl_client, deepl_config):
        """Test successful single text translation."""
        # Setup mock
        mock_result = Mock()
        mock_result.text = "¡Hola mundo!"
        mock_result.detected_source_lang = "EN"
        
        mock_client_instance = Mock()
        mock_client_instance.translate_text.return_value = mock_result
        mock_deepl_client.return_value = mock_client_instance
        
        translator = DeepLTranslator(deepl_config)
        result = translator.translate("Hello world", "en", "es")
        
        assert result["translated_text"] == "¡Hola mundo!"
        assert result["status"] == TranslationStatus.SUCCESS
        assert result["metadata"]["detected_language"] == "en"
        assert result["metadata"]["provider"] == "deepl"

    @patch('deepl.Translator')
    def test_translate_empty_text(self, mock_deepl_client, deepl_config):
        """Test translation of empty text."""
        translator = DeepLTranslator(deepl_config)
        result = translator.translate("", "en", "es")
        
        assert result["translated_text"] == ""
        assert result["status"] == TranslationStatus.SUCCESS
        assert result["char_count"] == 0

    @patch('deepl.Translator')
    def test_translate_text_too_long(self, mock_deepl_client, deepl_config):
        """Test translation with text exceeding character limit."""
        translator = DeepLTranslator(deepl_config)
        long_text = "a" * 30001  # Exceeds max_chunk_size
        
        result = translator.translate(long_text, "en", "es")
        assert result["status"] == TranslationStatus.ERROR
        assert "exceeds DeepL's maximum" in result["error"]

    @patch('deepl.Translator')
    def test_translate_with_auto_detect(self, mock_deepl_client, deepl_config):
        """Test translation with automatic language detection."""
        mock_result = Mock()
        mock_result.text = "¡Hola mundo!"
        mock_result.detected_source_lang = "EN"
        
        mock_client_instance = Mock()
        mock_client_instance.translate_text.return_value = mock_result
        mock_deepl_client.return_value = mock_client_instance
        
        translator = DeepLTranslator(deepl_config)
        result = translator.translate("Hello world", "auto", "es")
        
        # Verify source_lang=None was passed (auto detection)
        call_args = mock_client_instance.translate_text.call_args
        assert call_args[1]["source_lang"] is None

    @patch('deepl.Translator')
    def test_translate_deepl_api_error(self, mock_deepl_client, deepl_config):
        """Test handling of DeepL API errors."""
        import deepl
        
        mock_client_instance = Mock()
        mock_client_instance.translate_text.side_effect = deepl.DeepLException(
            "API quota exceeded"
        )
        mock_deepl_client.return_value = mock_client_instance
        
        translator = DeepLTranslator(deepl_config)
        result = translator.translate("Hello", "en", "es")
        
        assert result["status"] == TranslationStatus.ERROR
        assert "DeepL API error" in result["error"]


class TestBulkTranslation:
    """Test bulk translation methods."""

    @patch('deepl.Translator')
    def test_bulk_translate_success(self, mock_deepl_client, deepl_config):
        """Test successful bulk translation."""
        # Setup mock responses
        mock_results = []
        texts = ["Hello", "Goodbye", "Thank you"]
        translations = ["Hola", "Adiós", "Gracias"]
        
        for translation in translations:
            result = Mock()
            result.text = translation
            result.detected_source_lang = "EN"
            mock_results.append(result)
        
        mock_client_instance = Mock()
        mock_client_instance.translate_text.return_value = mock_results
        mock_deepl_client.return_value = mock_client_instance
        
        translator = DeepLTranslator(deepl_config)
        results = translator.bulk_translate(texts, "en", "es")
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result["translated_text"] == translations[i]
            assert result["status"] == TranslationStatus.SUCCESS

    @patch('deepl.Translator')
    def test_bulk_translate_empty_list(self, mock_deepl_client, deepl_config):
        """Test bulk translation with empty list."""
        translator = DeepLTranslator(deepl_config)
        results = translator.bulk_translate([], "en", "es")
        assert results == []

    @patch('deepl.Translator')
    def test_bulk_translate_with_empty_texts(self, mock_deepl_client, deepl_config):
        """Test bulk translation with some empty texts."""
        mock_result = Mock()
        mock_result.text = "Hola"
        mock_result.detected_source_lang = "EN"
        
        mock_client_instance = Mock()
        mock_client_instance.translate_text.return_value = [mock_result]
        mock_deepl_client.return_value = mock_client_instance
        
        translator = DeepLTranslator(deepl_config)
        texts = ["Hello", "", "World"]
        results = translator.bulk_translate(texts, "en", "es")
        
        assert len(results) == 3
        assert results[0]["translated_text"] == "Hola"
        assert results[1]["translated_text"] == ""  # Empty text
        assert results[2]["translated_text"] == "Hola"  # Second valid text


class TestAsyncTranslation:
    """Test asynchronous translation methods."""

    @pytest.mark.asyncio
    async def test_translate_async_success(self, deepl_config, deepl_response_single):
        """Test successful async translation."""
        with patch('aiohttp.ClientSession') as mock_session:
            # Setup mock response
            mock_response = AsyncMock()
            mock_response.json.return_value = deepl_response_single
            mock_response.raise_for_status.return_value = None
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            translator = DeepLTranslator(deepl_config)
            result = await translator.translate_async("Hello world", "en", "es")
            
            assert result["translated_text"] == "¡Hola mundo!"
            assert result["status"] == TranslationStatus.SUCCESS
            assert result["metadata"]["detected_language"] == "en"

    @pytest.mark.asyncio
    async def test_bulk_translate_async_success(self, deepl_config, deepl_response_bulk):
        """Test successful async bulk translation."""
        with patch('aiohttp.ClientSession') as mock_session:
            # Setup mock response
            mock_response = AsyncMock()
            mock_response.json.return_value = deepl_response_bulk
            mock_response.raise_for_status.return_value = None
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            translator = DeepLTranslator(deepl_config)
            texts = ["Hello world", "How are you?", "Goodbye"]
            results = await translator.bulk_translate_async(texts, "en", "es")
            
            assert len(results) == 3
            expected_translations = ["¡Hola mundo!", "¿Cómo estás?", "¡Adiós!"]
            for i, result in enumerate(results):
                assert result["translated_text"] == expected_translations[i]
                assert result["status"] == TranslationStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_translate_async_api_error(self, deepl_config):
        """Test async translation API error handling."""
        import aiohttp
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.side_effect = aiohttp.ClientError("Connection failed")
            
            translator = DeepLTranslator(deepl_config)
            result = await translator.translate_async("Hello", "en", "es")
            
            assert result["status"] == TranslationStatus.ERROR
            assert "DeepL API error" in result["error"]


class TestAdditionalMethods:
    """Test additional utility methods."""

    @patch('deepl.Translator')
    def test_get_supported_languages_success(self, mock_deepl_client, deepl_config):
        """Test successful retrieval of supported languages."""
        # Setup mock language objects
        mock_source_lang = Mock()
        mock_source_lang.code = "EN"
        mock_target_lang = Mock()
        mock_target_lang.code = "ES"
        
        mock_client_instance = Mock()
        mock_client_instance.get_source_languages.return_value = [mock_source_lang]
        mock_client_instance.get_target_languages.return_value = [mock_target_lang]
        mock_deepl_client.return_value = mock_client_instance
        
        translator = DeepLTranslator(deepl_config)
        languages = translator.get_supported_languages()
        
        assert "source" in languages
        assert "target" in languages
        assert "en" in languages["source"]
        assert "es" in languages["target"]

    @patch('deepl.Translator')
    def test_get_supported_languages_fallback(self, mock_deepl_client, deepl_config):
        """Test fallback when language retrieval fails."""
        mock_client_instance = Mock()
        mock_client_instance.get_source_languages.side_effect = Exception("API Error")
        mock_deepl_client.return_value = mock_client_instance
        
        translator = DeepLTranslator(deepl_config)
        languages = translator.get_supported_languages()
        
        # Should return fallback language list
        assert "source" in languages
        assert "target" in languages
        assert len(languages["source"]) > 0
        assert len(languages["target"]) > 0

    @patch('deepl.Translator')
    def test_get_usage_info_success(self, mock_deepl_client, deepl_config):
        """Test successful usage info retrieval."""
        # Setup mock usage object
        mock_character = Mock()
        mock_character.count = 12345
        mock_character.limit = 500000
        mock_character.limit_reached = False
        
        mock_usage = Mock()
        mock_usage.character = mock_character
        
        mock_client_instance = Mock()
        mock_client_instance.get_usage.return_value = mock_usage
        mock_deepl_client.return_value = mock_client_instance
        
        translator = DeepLTranslator(deepl_config)
        usage = translator.get_usage_info()
        
        assert usage["character_count"] == 12345
        assert usage["character_limit"] == 500000
        assert usage["character_limit_reached"] is False

    @patch('deepl.Translator')
    def test_get_usage_info_error(self, mock_deepl_client, deepl_config):
        """Test usage info retrieval error handling."""
        mock_client_instance = Mock()
        mock_client_instance.get_usage.side_effect = Exception("API Error")
        mock_deepl_client.return_value = mock_client_instance
        
        translator = DeepLTranslator(deepl_config)
        usage = translator.get_usage_info()
        
        # Should return empty dict on error
        assert usage == {}


class TestErrorHandling:
    """Test comprehensive error handling scenarios."""

    @patch('deepl.Translator')
    def test_general_exception_handling(self, mock_deepl_client, deepl_config):
        """Test handling of general exceptions."""
        mock_client_instance = Mock()
        mock_client_instance.translate_text.side_effect = ValueError("Invalid input")
        mock_deepl_client.return_value = mock_client_instance
        
        translator = DeepLTranslator(deepl_config)
        result = translator.translate("Hello", "en", "es")
        
        assert result["status"] == TranslationStatus.ERROR
        assert "Invalid input" in result["error"]


class TestProviderDiscovery:
    """Test provider discovery and integration."""

    def test_provider_discovery(self, deepl_config):
        """Test that the provider can be discovered."""
        from mt_providers import get_provider
        
        provider_class = get_provider("deepl")
        translator = provider_class(deepl_config)
        
        assert isinstance(translator, DeepLTranslator)
        assert translator.name == "deepl"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
