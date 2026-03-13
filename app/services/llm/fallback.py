import logging
from typing import Any

from app.services.llm.base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class FallbackLLMProvider(BaseLLMProvider):
    """Tries each provider in order, falling back to the next on failure."""

    def __init__(self, providers: list[BaseLLMProvider], names: list[str]):
        self._providers = providers
        self._names = names

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        last_exc: Exception | None = None
        for name, provider in zip(self._names, self._providers, strict=True):
            try:
                return await provider.chat_completion(messages, tools, temperature)
            except Exception as exc:
                logger.warning("LLM provider '%s' failed, trying next: %s", name, exc)
                last_exc = exc
        raise RuntimeError(f"All LLM providers failed. Last error: {last_exc}") from last_exc

    async def parse_structured(
        self,
        messages: list[dict[str, str]],
        response_format: type,
        temperature: float = 0.3,
    ) -> Any:
        last_exc: Exception | None = None
        for name, provider in zip(self._names, self._providers, strict=True):
            try:
                return await provider.parse_structured(messages, response_format, temperature)
            except Exception as exc:
                logger.warning("LLM provider '%s' failed, trying next: %s", name, exc)
                last_exc = exc
        raise RuntimeError(f"All LLM providers failed. Last error: {last_exc}") from last_exc
