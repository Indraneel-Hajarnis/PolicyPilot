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


def translate_and_expand_query(query: str, target_lang: str = "mr") -> str:
    """
    Expand query with cross-lingual Marathi terms to ensure robust retrieval over Marathi PDFs.
    """
    query_clean = query.strip()
    expansions = [query_clean]

    # Heuristic glossary lookup
    query_lower = query_clean.lower()
    for eng_term, mr_term in MARATHI_GOVT_GLOSSARY.items():
        if eng_term in query_lower:
            expansions.append(mr_term)

    # Use LLM query rewrite if API key is present
    if settings.api_key:
        try:
            from app.services.groq_client import GroqClient
            client = GroqClient(api_key=settings.api_key)
            prompt = (
                f"Rewrite this user query into a concise search query containing both English and Marathi (Devanagari) terms for government resolutions (GRs).\n"
                f"User Question: \"{query_clean}\"\n"
                f"Return ONLY the rewritten query line, nothing else."
            )
            llm_expanded = client.generate(prompt, model="llama-3.1-8b-instant").strip()
            if llm_expanded and len(llm_expanded) < 250:
                expansions.append(llm_expanded)
        except Exception as exc:
            logger.warning("LLM query expansion failed: %s", exc)

    return " ".join(dict.fromkeys(expansions))

