"""DeepL translation provider implementation."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import aiohttp
import deepl
from mt_providers.base import BaseTranslationProvider
from mt_providers.exceptions import TranslationError
from mt_providers.types import TranslationConfig, TranslationResponse

logger = logging.getLogger(__name__)


class DeepLTranslator(BaseTranslationProvider):
    """DeepL API provider implementation."""

    name = "deepl"
    requires_region = False  # DeepL doesn't require region
    supports_async = True
    min_supported_version = "0.1.8"
    max_chunk_size = 30000  # DeepL's character limit per request

    def __init__(self, config: TranslationConfig) -> None:
        """Initialize DeepL translator with configuration."""
        super().__init__(config)

        # Initialize DeepL client
        self._client: Optional[deepl.Translator] = None
        self._async_session: Optional[aiohttp.ClientSession] = None

        # DeepL API endpoint configuration
        self.is_free_api = self._is_free_api_key(config.api_key)
        self.base_url = self._get_api_endpoint()

    def _is_free_api_key(self, api_key: str) -> bool:
        """Determine if API key is for free or pro tier."""
        return api_key.endswith(":fx")

    def _get_api_endpoint(self) -> str:
        """Get appropriate API endpoint based on API key type."""
        if self.is_free_api:
            return "https://api-free.deepl.com"
        return "https://api.deepl.com"

    @property
    def client(self) -> deepl.Translator:
        """Get or create DeepL client."""
        if self._client is None:
            endpoint = None
            if hasattr(self.config, 'endpoint') and self.config.endpoint:
                endpoint = self.config.endpoint

            self._client = deepl.Translator(
                auth_key=self.config.api_key,
                server_url=endpoint or self.base_url
            )
        return self._client

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers for direct API calls."""
        return {
            "Authorization": f"DeepL-Auth-Key {self.config.api_key}",
            "Content-Type": "application/json",
            "User-Agent": self.get_user_agent()  # Uses base class method
        }

    def _get_root_lang_code(self, lang_code: str) -> str:
        if '-' in lang_code:
            return lang_code.split('-')[0].lower()
        return lang_code


    def _map_language_code(self, lang_code: str) -> str:
        """Map language codes to DeepL format."""
        # DeepL language mapping
        supported_language_map = {
            "ar": "AR",
            "bg": "BG",
            "cs": "CS",
            "da": "DA",
            "de": "DE",
            "el": "EL",
            "en": "EN",
            "en-GB": "EN-GB",
            "en-US": "EN-US",
            "es": "ES",
            "es-419": "ES-419",
            "et": "ET",
            "fi": "FI",
            "fr": "FR",
            "he": "HE",
            "hu": "HU",
            "id": "ID",
            "it": "IT",
            "ja": "JA",
            "ko": "KO",
            "lt": "LT",
            "lv": "LV",
            "nb": "NB",
            "nl": "NL",
            "pl": "PL",
            "pt": "PT",
            "pt-BR": "PT-BR",
            "pt-PT": "PT-PT",
            "ro": "RO",
            "ru": "RU",
            "sk": "SK",
            "sl": "SL",
            "sv": "SV",
            "th": "TH",
            "tr": "TR",
            "uk": "UK",
            "vi": "VI",
            "zh": "ZH",
            "zh-HANS": "ZH-HANS",
            "zh-HANT": "ZH-HANT"
        }

        # Check if we have a specific mapping
        if lang_code in supported_language_map:
            return supported_language_map[lang_code]
        raise ValueError('Unsupported Language')

    def translate(
        self, text: str, source_lang: str, target_lang: str
    ) -> TranslationResponse:
        """Translate single text using DeepL API."""
        try:
            # Validate input
            if not text.strip():
                return self._create_response(
                    translated_text="",
                    source_lang=source_lang,
                    target_lang=target_lang,
                    char_count=0
                )

            if len(text) > self.max_chunk_size:
                error_msg = (
                    f"Text length ({len(text)}) exceeds DeepL's maximum "
                    f"of {self.max_chunk_size} characters"
                )
                raise TranslationError(error_msg)

            # Map language codes
            source_mapped = None
            if source_lang != "auto":
                source_mapped = self._map_language_code(
                    self._get_root_lang_code(source_lang))
            try:
                target_mapped = self._map_language_code(target_lang)
            except ValueError:
                target_mapped = self._map_language_code(
                    self._get_root_lang_code(target_lang)
                )

            # Perform translation using DeepL SDK
            result = self.client.translate_text(
                text=text,
                source_lang=source_mapped,
                target_lang=target_mapped
            )

            # Extract metadata
            detected_lang = source_lang
            if result.detected_source_lang:
                detected_lang = result.detected_source_lang.lower()

            return self._create_response(
                translated_text=result.text,
                source_lang=source_lang,
                target_lang=target_lang,
                char_count=len(text),
                metadata={
                    "detected_language": detected_lang,
                    "confidence": 1.0,  # DeepL doesn't provide scores
                    "provider": "deepl",
                    "model": "deepl-api",
                    "billed_characters": len(text)
                }
            )

        except deepl.DeepLException as e:
            logger.error(f"DeepL API error: {str(e)}")
            return self._create_response(
                translated_text="",
                source_lang=source_lang,
                target_lang=target_lang,
                char_count=len(text),
                error=f"DeepL API error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return self._create_response(
                translated_text="",
                source_lang=source_lang,
                target_lang=target_lang,
                char_count=len(text),
                error=str(e)
            )

    def bulk_translate(
        self, texts: List[str], source_lang: str, target_lang: str
    ) -> List[TranslationResponse]:
        """Translate multiple texts using DeepL API."""
        if not texts:
            return []

        try:
            # Filter out empty texts but maintain positions
            text_mapping = {}
            valid_texts = []

            for i, text in enumerate(texts):
                if text.strip():
                    text_mapping[len(valid_texts)] = i
                    valid_texts.append(text)

            if not valid_texts:
                return [
                    self._create_response("", source_lang, target_lang, 0)
                    for _ in texts
                ]

            if source_lang != "auto":
                source_mapped = self._map_language_code(
                    self._get_root_lang_code(source_lang))
            else:
                source_mapped = None
            try:
                target_mapped = self._map_language_code(target_lang)
            except ValueError:
                target_mapped = self._map_language_code(
                    self._get_root_lang_code(target_lang)
                )

            # Perform bulk translation
            results = self.client.translate_text(
                text=valid_texts,
                source_lang=source_mapped,
                target_lang=target_mapped
            )

            # Ensure results is a list
            if not isinstance(results, list):
                results = [results]

            # Create response mapping
            responses = [None] * len(texts)

            for i, result in enumerate(results):
                original_index = text_mapping[i]
                detected_lang = result.detected_source_lang.lower() if result.detected_source_lang else source_lang

                responses[original_index] = self._create_response(
                    translated_text=result.text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    char_count=len(texts[original_index]),
                    metadata={
                        "detected_language": detected_lang,
                        "confidence": 1.0,
                        "provider": "deepl",
                        "model": "deepl-api",
                        "billed_characters": len(texts[original_index])
                    }
                )
                
            # Fill in empty responses for empty texts
            for i, response in enumerate(responses):
                if response is None:
                    responses[i] = self._create_response("", source_lang, target_lang, 0)
                    
            return responses
            
        except deepl.DeepLException as e:
            logger.error(f"DeepL bulk translation error: {str(e)}")
            return [
                self._create_response(
                    translated_text="",
                    source_lang=source_lang,
                    target_lang=target_lang,
                    char_count=len(text),
                    error=f"DeepL API error: {str(e)}"
                )
                for text in texts
            ]
        except Exception as e:
            logger.error(f"Bulk translation error: {str(e)}")
            return [
                self._create_response(
                    translated_text="",
                    source_lang=source_lang,
                    target_lang=target_lang,
                    char_count=len(text),
                    error=str(e)
                )
                for text in texts
            ]

    async def translate_async(
        self, text: str, source_lang: str, target_lang: str
    ) -> TranslationResponse:
        """Async translate single text using DeepL API."""
        try:
            # Validate input
            if not text.strip():
                return self._create_response(
                    translated_text="",
                    source_lang=source_lang,
                    target_lang=target_lang,
                    char_count=0
                )

            if len(text) > self.max_chunk_size:
                raise TranslationError(
                    f"Text length ({len(text)}) exceeds DeepL's maximum of {self.max_chunk_size} characters"
                )

            if source_lang != "auto":
                source_mapped = self._map_language_code(
                    self._get_root_lang_code(source_lang))
            else:
                source_mapped = None
            try:
                target_mapped = self._map_language_code(target_lang)
            except ValueError:
                target_mapped = self._map_language_code(
                    self._get_root_lang_code(target_lang)
                )
            # Prepare request data
            data = {
                "text": [text],
                "target_lang": target_mapped
            }

            if source_mapped:
                data["source_lang"] = source_mapped

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v2/translate",
                    headers=self._get_headers(),
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

            # Extract translation result
            translation = result["translations"][0]
            detected_lang = translation.get("detected_source_language", source_lang).lower()

            return self._create_response(
                translated_text=translation["text"],
                source_lang=source_lang,
                target_lang=target_lang,
                char_count=len(text),
                metadata={
                    "detected_language": detected_lang,
                    "confidence": 1.0,
                    "provider": "deepl",
                    "model": "deepl-api",
                    "billed_characters": len(text)
                }
            )

        except aiohttp.ClientError as e:
            logger.error(f"DeepL async API error: {str(e)}")
            return self._create_response(
                translated_text="",
                source_lang=source_lang,
                target_lang=target_lang,
                char_count=len(text),
                error=f"DeepL API error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Async translation error: {str(e)}")
            return self._create_response(
                translated_text="",
                source_lang=source_lang,
                target_lang=target_lang,
                char_count=len(text),
                error=str(e)
            )

    async def bulk_translate_async(
        self, texts: List[str], source_lang: str, target_lang: str
    ) -> List[TranslationResponse]:
        """Async translate multiple texts using DeepL API."""
        if not texts:
            return []

        try:
            # Filter out empty texts but maintain positions
            text_mapping = {}
            valid_texts = []

            for i, text in enumerate(texts):
                if text.strip():
                    text_mapping[len(valid_texts)] = i
                    valid_texts.append(text)

            if not valid_texts:
                return [
                    self._create_response("", source_lang, target_lang, 0)
                    for _ in texts
                ]

            # Map language codes
            if source_lang != "auto":
                source_mapped = self._map_language_code(
                    self._get_root_lang_code(source_lang))
            else:
                source_mapped = None
            try:
                target_mapped = self._map_language_code(target_lang)
            except ValueError:
                target_mapped = self._map_language_code(
                    self._get_root_lang_code(target_lang)
                )
            # Prepare request data
            data = {
                "text": valid_texts,
                "target_lang": target_mapped
            }

            if source_mapped:
                data["source_lang"] = source_mapped

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v2/translate",
                    headers=self._get_headers(),
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

            # Create response mapping
            responses = [None] * len(texts)

            for i, translation in enumerate(result["translations"]):
                original_index = text_mapping[i]
                detected_lang = translation.get("detected_source_language", source_lang).lower()

                responses[original_index] = self._create_response(
                    translated_text=translation["text"],
                    source_lang=source_lang,
                    target_lang=target_lang,
                    char_count=len(texts[original_index]),
                    metadata={
                        "detected_language": detected_lang,
                        "confidence": 1.0,
                        "provider": "deepl",
                        "model": "deepl-api",
                        "billed_characters": len(texts[original_index])
                    }
                )

            # Fill in empty responses for empty texts
            for i, response in enumerate(responses):
                if response is None:
                    responses[i] = self._create_response("", source_lang, target_lang, 0)

            return responses

        except aiohttp.ClientError as e:
            logger.error(f"DeepL async bulk translation error: {str(e)}")
            return [
                self._create_response(
                    translated_text="",
                    source_lang=source_lang,
                    target_lang=target_lang,
                    char_count=len(text),
                    error=f"DeepL API error: {str(e)}"
                )
                for text in texts
            ]
        except Exception as e:
            logger.error(f"Async bulk translation error: {str(e)}")
            return [
                self._create_response(
                    translated_text="",
                    source_lang=source_lang,
                    target_lang=target_lang,
                    char_count=len(text),
                    error=str(e)
                )
                for text in texts
            ]

    def get_supported_languages(self) -> Dict[str, List[str]]:
        """Get supported source and target languages from DeepL."""
        try:
            source_langs = self.client.get_source_languages()
            target_langs = self.client.get_target_languages()

            return {
                "source": [lang.code.lower() for lang in source_langs],
                "target": [lang.code.lower() for lang in target_langs]
            }
        except Exception as e:
            logger.error(f"Error fetching supported languages: {str(e)}")
            # Return common DeepL languages as fallback
            return {
                "source": ["en", "de", "fr", "es", "pt", "it", "ru", "ja", "zh", "pl", "nl", "sv", "da", "no", "fi"],
                "target": ["en-us", "en-gb", "de", "fr", "es", "pt-pt", "pt-br", "it", "ru", "ja", "zh", "pl", "nl", "sv", "da", "no", "fi"]
            }

    def get_usage_info(self) -> Dict[str, Any]:
        """Get current usage information from DeepL."""
        try:
            usage = self.client.get_usage()
            return {
                "character_count": usage.character.count,
                "character_limit": usage.character.limit,
                "character_limit_reached": usage.character.limit_reached if hasattr(usage.character, 'limit_reached') else False,
                "document_count": usage.document.count if hasattr(usage, 'document') else 0,
                "document_limit": usage.document.limit if hasattr(usage, 'document') else 0,
                "team_document_count": usage.team_document.count if hasattr(usage, 'team_document') else 0,
                "team_document_limit": usage.team_document.limit if hasattr(usage, 'team_document') else 0,
            }
        except Exception as e:
            logger.error(f"Error fetching usage info: {str(e)}")
            return {}

    def __del__(self):
        """Cleanup resources."""
        if self._client:
            # DeepL client doesn't need explicit cleanup
            pass
        if self._async_session and not self._async_session.closed:
            # Note: In a real application, you should properly close async sessions
            # This is just a fallback cleanup
            pass
