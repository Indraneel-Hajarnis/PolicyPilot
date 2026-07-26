"""
Q&A prompt templates for the RAG pipeline.

Instructs the LLM to answer based on provided context, cite sources,
and include a confidence score.
"""

from app.services.language_utils import get_language_name
from app.services.retriever import RetrievalResult

SYSTEM_PROMPT = """You are PolicyPilot, an expert AI assistant specialized in analyzing policy documents. Your role is to answer questions accurately based ONLY on the provided document context.

## Rules
1. Answer the question using ONLY the information in the provided context chunks.
2. If the context does not contain enough information to answer the question, say so clearly. Do NOT make up information.
3. When referencing information, mention the source document name and page number.
4. Be precise, professional, and well-structured in your response.
5. Use markdown formatting for clarity (bullet points, bold for key terms, etc.).
6. At the very end of your response, on a new line, include your confidence score in the format: [CONFIDENCE: X.XX] where X.XX is a number between 0.00 and 1.00 representing how confident you are that your answer is correct and complete based on the available context.

## Confidence Guide
- 0.90-1.00: Answer is directly and clearly stated in the context
- 0.70-0.89: Answer is well-supported but requires some inference
- 0.50-0.69: Answer is partially supported, some aspects may be uncertain
- 0.30-0.49: Answer is weakly supported, significant uncertainty
- 0.00-0.29: Very little relevant information found"""


def build_qa_messages(
    question: str,
    context_chunks: list[RetrievalResult],
    language: str | None = None,
) -> list[dict[str, str]]:
    """
    Build the chat messages for a Q&A completion.

    Args:
        question: The user's question.
        context_chunks: Retrieved context chunks with metadata.
        language: Optional target language for the response.

    Returns:
        List of message dicts for the Groq API.
    """
    # Build context section
    if context_chunks:
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            context_parts.append(
                f"--- Source {i}: \"{chunk.document_name}\" (Page {chunk.page_number}, "
                f"Relevance: {chunk.score:.2f}) ---\n{chunk.content}"
            )
        context_text = "\n\n".join(context_parts)
    else:
        context_text = "No relevant context was found in the uploaded documents."

    # Build user message
    user_message = f"## Context from Policy Documents\n\n{context_text}\n\n## Question\n\n{question}"

    # Add language instruction if needed
    system = SYSTEM_PROMPT
    if language and language != "en":
        lang_name = get_language_name(language)
        system += f"\n\n## Language Requirement\nYou MUST respond entirely in {lang_name}. Ensure smooth, natural phrasing in {lang_name}. However, keep the exact meta tag [CONFIDENCE: X.XX] at the end in English."

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_message},
    ]
