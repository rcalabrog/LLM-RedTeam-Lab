from functools import lru_cache

from ..core.config import Settings
from .base import LLMProvider
from .ollama_provider import OllamaProvider


class UnsupportedProviderError(ValueError):
    """Raised when requested provider is not registered."""


def _normalize_provider_name(name: str) -> str:
    return name.strip().lower()


@lru_cache
def _build_provider_cached(
    provider_name: str, ollama_base_url: str, timeout_seconds: float
) -> LLMProvider:
    normalized = _normalize_provider_name(provider_name)
    if normalized == "ollama":
        return OllamaProvider(base_url=ollama_base_url, timeout_seconds=timeout_seconds)
    raise UnsupportedProviderError(f"Unsupported LLM provider: '{provider_name}'.")


def get_llm_provider(settings: Settings) -> LLMProvider:
    """
    Return the configured LLM provider instance.

    Cache key is derived from settings values so changing env/config yields
    a new provider instance while preserving reuse within a process.
    """
    return _build_provider_cached(
        provider_name=settings.llm_provider,
        ollama_base_url=settings.ollama_base_url,
        timeout_seconds=settings.llm_request_timeout_seconds,
    )
