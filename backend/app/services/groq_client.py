"""
Groq API client wrapper.

Provides sync and async methods for chat completions with retry logic.
"""

import asyncio
from typing import Any

from groq import Groq

from app.config import settings
from app.core.exceptions import LLMError
from app.core.logging_config import get_logger

logger = get_logger("services.groq_client")


class GroqClient:
    """Wrapper around the Groq Python SDK for LLM chat completions."""

    _instance: "GroqClient | None" = None
    _client: Groq | None = None

    def __new__(cls) -> "GroqClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _ensure_client(self) -> None:
        """Initialize the Groq client if not already done."""
        if self._client is None:
            if not settings.groq_api_key:
                raise LLMError("GROQ_API_KEY is not set in environment")
            self._client = Groq(api_key=settings.groq_api_key)
            logger.info("Groq client initialized (model: %s)", settings.groq_model)

    @property
    def client(self) -> Groq:
        self._ensure_client()
        return self._client  # type: ignore[return-value]

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2048,
        model: str | None = None,
    ) -> str:
        """
        Send a chat completion request to the Groq API.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Maximum tokens in the response.
            model: Override the default model.

        Returns:
            The assistant's response text.

        Raises:
            LLMError: If the API call fails after retries.
        """
        model = model or settings.groq_model

        for attempt in range(3):
            try:
                # Run the sync Groq client in a thread pool
                response = await asyncio.to_thread(
                    self._create_completion,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model=model,
                )

                content = response.choices[0].message.content
                logger.info(
                    "Groq response received (model=%s, tokens=%d)",
                    model,
                    response.usage.completion_tokens if response.usage else 0,
                )
                return content or ""

            except LLMError:
                raise
            except Exception as e:
                logger.warning(
                    "Groq API attempt %d/3 failed: %s", attempt + 1, str(e)
                )
                if attempt == 2:
                    raise LLMError(f"All retry attempts failed: {e}")
                await asyncio.sleep(1.0 * (attempt + 1))

        raise LLMError("Unexpected retry loop exit")

    def _create_completion(self, **kwargs: Any) -> Any:
        """Synchronous completion call for thread pool execution."""
        return self.client.chat.completions.create(**kwargs)


# Module-level singleton
groq_client = GroqClient()
