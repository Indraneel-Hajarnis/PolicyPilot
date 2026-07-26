def build_summary_prompt(text: str) -> str:
    return f"Summarize the following document in a structured format with key points and risks:\n\n{text}"
