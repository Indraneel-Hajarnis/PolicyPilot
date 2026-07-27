import os
import requests
from app.config import settings


class GroqClient:
    def __init__(self, api_key: str | None = None):
        self._api_key = api_key

    @property
    def api_key(self) -> str:
        return self._api_key or settings.api_key

    def generate(self, prompt: str, model: str | None = None) -> str:
        key = self.api_key
        if not key:
            raise ValueError("Groq API key is empty or not configured.")

        requested_model = model or settings.model_name or "llama-3.3-70b-versatile"
        models_to_try = [requested_model]
        for fallback in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

        last_error = None
        for m in models_to_try:
            payload = {
                "model": m,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30,
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except Exception as err:
                last_error = err
                continue

        if last_error:
            raise last_error
        raise RuntimeError("Failed to generate response from Groq LLM.")
