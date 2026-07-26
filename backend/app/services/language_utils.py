"""
Language detection and translation utilities.

Uses langdetect for detection and the Groq LLM for translation.
"""

# pyrefly: ignore [missing-import]
from langdetect import detect, LangDetectException

from app.core.logging_config import get_logger
from app.services.groq_client import groq_client

logger = get_logger("services.language_utils")

# Primary supported languages: English, Hindi, Marathi
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "ru": "Russian",
}


def detect_language(text: str) -> str:
    """
    Detect the language of a text string.

    Args:
        text: Input text to detect.

    Returns:
        ISO 639-1 language code (e.g., "en", "fr", "es").
        Defaults to "en" on detection failure.
    """
    if not text or len(text.strip()) < 10:
        return "en"

    try:
        lang = detect(text)
        logger.debug("Detected language: %s", lang)
        return lang
    except LangDetectException:
        logger.warning("Language detection failed, defaulting to 'en'")
        return "en"


def get_language_name(code: str) -> str:
    """Return the human-readable name for a language code."""
    return LANGUAGE_NAMES.get(code, code.upper())


async def translate_text(
    text: str,
    target_language: str,
    source_language: str | None = None,
) -> str:
    """
    Translate text to the target language using the Groq LLM.

    Args:
        text: Text to translate.
        target_language: Target language code (ISO 639-1).
        source_language: Optional source language code.

    Returns:
        Translated text string.
    """
    if not text:
        return text

    # Detect source language if not provided
    if source_language is None:
        source_language = detect_language(text)

    # No translation needed if same language
    if source_language == target_language:
        return text

    target_name = get_language_name(target_language)
    source_name = get_language_name(source_language)

    messages = [
        {
            "role": "system",
            "content": (
                f"You are a professional translator. Translate the following text "
                f"from {source_name} to {target_name}. "
                f"Preserve the original meaning, tone, and formatting. "
                f"Return ONLY the translated text, nothing else."
            ),
        },
        {"role": "user", "content": text},
    ]

    translated = await groq_client.chat_completion(
        messages=messages,
        temperature=0.1,
        max_tokens=4000,
    )

    logger.info("Translated text from %s to %s", source_name, target_name)
    return translated
