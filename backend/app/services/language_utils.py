def detect_language(text: str) -> str:
    """Detect language from text. Returns 'en', 'hi', or 'mr'."""
    if not text or not text.strip():
        return "en"

    # Check for Devanagari script characters (covers both Hindi and Marathi)
    devanagari_count = sum(1 for c in text[:500] if "\u0900" <= c <= "\u097F")
    total = min(len(text), 500)

    if devanagari_count / total > 0.15:
        # Try langdetect for more precise hi vs mr detection
        try:
            # pyrefly: ignore [missing-import]
            from langdetect import detect
            lang = detect(text[:1000])
            if lang == "mr":
                return "mr"
            return "hi"  # Default Devanagari to Hindi
        except Exception:
            return "hi"

    # Try langdetect for other languages
    try:
        # pyrefly: ignore [missing-import]
        from langdetect import detect
        lang = detect(text[:1000])
        if lang in ("hi", "mr"):
            return lang
        return "en"
    except Exception:
        return "en"


def translate_text(text: str, target_language: str) -> str:
    """Placeholder — translation is handled by the Groq LLM via prompt."""
    return text
