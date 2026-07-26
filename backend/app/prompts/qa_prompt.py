def build_qa_prompt(question: str, context: str) -> str:
    return f"Question: {question}\n\nContext:\n{context}\n\nAnswer concisely and cite the relevant context."
