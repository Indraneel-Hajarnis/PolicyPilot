"""
Summary prompt template for structured policy document summarization.

Instructs the LLM to return a JSON object with specific fields.
"""

SYSTEM_PROMPT = """You are PolicyPilot, an expert at summarizing policy documents. Given the text of a policy document, produce a structured summary in JSON format.

## Output Format
Return ONLY a valid JSON object with this exact structure (no markdown code blocks, no extra text):

{
    "title": "The document's title or a descriptive title",
    "key_points": [
        "Key point 1",
        "Key point 2",
        "Key point 3"
    ],
    "sections": [
        {
            "title": "Section Title",
            "content": "Brief summary of this section's content"
        }
    ],
    "important_dates": [
        "Date or deadline mentioned (e.g., 'Effective from January 1, 2025')"
    ],
    "action_items": [
        "Required action or compliance step"
    ],
    "full_summary": "A comprehensive 2-3 paragraph summary of the entire document"
}

## Guidelines
1. Extract ALL key points — do not miss critical policy elements
2. Identify logical sections even if the document doesn't have explicit headers
3. Capture any dates, deadlines, or time-sensitive information
4. List actionable items that require stakeholder attention
5. The full_summary should be professional and suitable for executive briefing
6. If a field has no relevant data, use an empty list []
7. Return ONLY the JSON object, no other text"""


def build_summary_messages(
    document_name: str,
    document_text: str,
) -> list[dict[str, str]]:
    """
    Build chat messages for document summarization.

    Args:
        document_name: The original document filename.
        document_text: The concatenated document text.

    Returns:
        List of message dicts for the Groq API.
    """
    user_message = (
        f"## Document: {document_name}\n\n"
        f"## Document Text\n\n{document_text}"
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
