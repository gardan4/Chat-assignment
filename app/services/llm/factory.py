import logging

from app.config import Settings
from app.services.llm.azure_openai import AzureOpenAIProvider
from app.services.llm.base import BaseLLMProvider
from app.services.llm.fallback import FallbackLLMProvider
from app.services.llm.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

_PROVIDERS: dict[str, str] = {
    "azure_openai": "AzureOpenAIProvider",
    "openai": "OpenAIProvider",
    "auto": "FallbackLLMProvider (azure_openai → openai)",
}


def _build_azure(settings: Settings) -> AzureOpenAIProvider:
    return AzureOpenAIProvider(
        api_key=settings.azure_openai_api_key,
        endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
        deployment=settings.azure_openai_deployment,
    )


def _build_openai(settings: Settings) -> OpenAIProvider:
    return OpenAIProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )


def create_llm_provider(settings: Settings) -> BaseLLMProvider:
    """Factory that creates the configured LLM provider.

    Switch providers by setting LLM_PROVIDER in .env:
      - "azure_openai"  — Azure OpenAI only
      - "openai"        — OpenAI only
      - "auto"          — tries azure_openai first, falls back to openai
    """
    provider_name = settings.llm_provider.lower()

    if provider_name == "azure_openai":
        return _build_azure(settings)

    if provider_name == "openai":
        return _build_openai(settings)

    if provider_name == "auto":
        providers: list[BaseLLMProvider] = []
        names: list[str] = []

        if settings.azure_openai_api_key and settings.azure_openai_endpoint:
            providers.append(_build_azure(settings))
            names.append("azure_openai")

        if settings.openai_api_key:
            providers.append(_build_openai(settings))
            names.append("openai")

        if not providers:
            raise ValueError(
                "LLM_PROVIDER=auto but no provider credentials are configured. "
                "Set AZURE_OPENAI_API_KEY/ENDPOINT or OPENAI_API_KEY."
            )

        if len(providers) == 1:
            logger.info("LLM_PROVIDER=auto: only '%s' has credentials, using it directly", names[0])
            return providers[0]

        logger.info("LLM_PROVIDER=auto: fallback chain %s", " → ".join(names))
        return FallbackLLMProvider(providers, names)

    available = list(_PROVIDERS.keys())
    raise ValueError(f"Unknown LLM provider: {provider_name!r}. Available: {available}")
