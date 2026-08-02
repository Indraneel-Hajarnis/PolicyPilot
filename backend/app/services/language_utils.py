import logging
from app.config import settings

logger = logging.getLogger("language_utils")

MARATHI_GOVT_GLOSSARY = {
    "government resolution": "शासन निर्णय",
    "gr": "शासन निर्णय",
    "circular": "शासन परिपत्रक",
    "department": "विभाग",
    "finance": "वित्त विभाग",
    "education": "शिक्षण विभाग",
    "higher and technical education": "उच्च व तंत्र शिक्षण विभाग",
    "general administration": "सामान्य प्रशासन विभाग",
    "promotion": "पदोन्नती",
    "pension": "निवृत्तीवेतन",
    "pay scale": "वेतनमान",
    "allowance": "भत्ता",
    "order": "आदेश",
    "notification": "अधिसूचना",
    "amendment": "सुधारणा",
    "eligibility": "पात्रता",
    "scheme": "योजना",
    "scholarship": "शिष्यवृत्ती",
    "reservation": "आरक्षण",
    "recruitment": "भरती",
}


def detect_language(text: str) -> str:
    """Detect language from text. Returns 'en', 'hi', or 'mr'."""
    if not text or not text.strip():
        return "en"

    devanagari_count = sum(1 for c in text[:500] if "\u0900" <= c <= "\u097F")
    total = min(len(text), 500)

    if devanagari_count / total > 0.15:
        try:
            from langdetect import detect
            lang = detect(text[:1000])
            if lang == "mr":
                return "mr"
            return "hi"
        except Exception:
            return "mr" if "शासन" in text or "महाराष्ट्र" in text or "परिणाम" in text else "hi"

    try:
        from langdetect import detect
        lang = detect(text[:1000])
        if lang in ("hi", "mr"):
            return lang
        return "en"
    except Exception:
        return "en"


def translate_text(text: str, target_language: str) -> str:
    """Translate text using Groq LLM if configured, fallback to original text."""
    if not text or not text.strip() or target_language == "en":
        return text

    if settings.api_key:
        try:
            from app.services.groq_client import GroqClient
            client = GroqClient(api_key=settings.api_key)
            prompt = (
                f"Translate the following administrative text into {'Marathi (मराठी)' if target_language == 'mr' else 'Hindi (हिन्दी)'}. "
                f"Preserve official terms accurately. Output ONLY the translation without commentary.\n\n"
                f"TEXT:\n{text}"
            )
            return client.generate(prompt, model="llama-3.1-8b-instant").strip()
        except Exception as exc:
            logger.warning("Translation failed: %s", exc)

    return text


def translate_context_for_query(context_text: str, question_lang: str) -> str:
    """
    Translate retrieved document context into the question's language so the
    LLM can synthesise a grounded answer even when the PDF and the user speak
    different languages.

    Only calls the LLM when a real cross-lingual gap is detected; otherwise
    returns the original context unchanged.
    """
    if not context_text or not context_text.strip():
        return context_text

    # Detect the predominant language of the retrieved context
    context_lang = detect_language(context_text[:1500])

    # No mismatch → nothing to do
    if context_lang == question_lang:
        return context_text

    if not settings.api_key:
        return context_text  # Cannot translate without an LLM

    lang_names = {"en": "English", "hi": "Hindi (हिन्दी)", "mr": "Marathi (मराठी)"}
    target_name = lang_names.get(question_lang, "English")

    try:
        from app.services.groq_client import GroqClient
        client = GroqClient(api_key=settings.api_key)

        # Split context into manageable chunks (Groq models have context limits)
        # Translate at most ~6000 chars to avoid token overflow
        truncated = context_text[:6000]
        prompt = (
            f"You are a precise document translator. Translate the following government policy "
            f"document excerpts into {target_name}. Preserve all official terms, reference numbers, "
            f"dates, and section headings exactly. Maintain the original structure and formatting "
            f"(including [Doc #...] prefixes). Output ONLY the translated text, no commentary.\n\n"
            f"TEXT TO TRANSLATE:\n{truncated}"
        )
        translated = client.generate(prompt, model="llama-3.1-8b-instant").strip()
        if translated and len(translated) > 50:
            logger.info("Translated context from '%s' to '%s' (%d chars)",
                        context_lang, question_lang, len(translated))
            return translated
    except Exception as exc:
        logger.warning("Context translation failed: %s", exc)

    return context_text


def translate_and_expand_query(query: str, target_lang: str = "mr") -> str:
    """
    Expand query with cross-lingual terms in ALL supported languages (EN, HI, MR)
    so FAISS retrieval works regardless of the PDF's language.

    For example, a Hindi question will also include English and Marathi terms,
    ensuring chunks from English or Marathi PDFs are retrieved.
    """
    query_clean = query.strip()
    expansions = [query_clean]

    # Detect which language the query is actually in
    query_lang = detect_language(query_clean)

    # Heuristic glossary lookup (English → Marathi)
    query_lower = query_clean.lower()
    for eng_term, mr_term in MARATHI_GOVT_GLOSSARY.items():
        if eng_term in query_lower:
            expansions.append(mr_term)

    # Reverse glossary lookup (Marathi → English)
    for eng_term, mr_term in MARATHI_GOVT_GLOSSARY.items():
        if mr_term in query_clean:
            expansions.append(eng_term)

    # Use LLM to translate the query into the OTHER languages for cross-lingual retrieval
    if settings.api_key:
        try:
            from app.services.groq_client import GroqClient
            client = GroqClient(api_key=settings.api_key)

            # Build the translation targets based on the query's own language
            if query_lang == "en":
                translate_targets = "Marathi (मराठी) and Hindi (हिन्दी)"
            elif query_lang == "mr":
                translate_targets = "English and Hindi (हिन्दी)"
            elif query_lang == "hi":
                translate_targets = "English and Marathi (मराठी)"
            else:
                translate_targets = "English, Marathi (मराठी), and Hindi (हिन्दी)"

            prompt = (
                f"Rewrite this user query into a concise multi-lingual search query. "
                f"The original query is in {'English' if query_lang == 'en' else 'Marathi' if query_lang == 'mr' else 'Hindi'}. "
                f"Add equivalent key terms in {translate_targets} so the query can match documents in any of these languages. "
                f"Include official government terminology where applicable.\n"
                f"User Question: \"{query_clean}\"\n"
                f"Return ONLY the rewritten multi-lingual query line, nothing else."
            )
            llm_expanded = client.generate(prompt, model="llama-3.1-8b-instant").strip()
            if llm_expanded and len(llm_expanded) < 400:
                expansions.append(llm_expanded)
        except Exception as exc:
            logger.warning("LLM query expansion failed: %s", exc)

    return " ".join(dict.fromkeys(expansions))

