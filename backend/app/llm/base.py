from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from .schemas import GenerationRequest, GenerationResponse, ProviderHealth


class LLMProviderError(Exception):
    """Base exception for provider-layer failures."""


class LLMProviderConnectionError(LLMProviderError):
    """Raised when the provider cannot be reached."""


class LLMProviderTimeoutError(LLMProviderError):
    """Raised when a provider request times out."""


class LLMProviderResponseError(LLMProviderError):
    """Raised when a provider response is malformed or invalid."""


class LLMProvider(ABC):
    """Abstract provider interface for text generation backends."""

    provider_name: str

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate a text response for the given request."""

    async def stream_generate(self, request: GenerationRequest) -> AsyncIterator[str]:
        """
        Optional streaming hook for future phases.

        Streaming is intentionally not implemented in this phase.
        """
        raise NotImplementedError(f"{self.provider_name} does not implement streaming yet.")

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Return provider availability for diagnostics."""
