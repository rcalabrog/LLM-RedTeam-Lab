import unittest

from app.core.config import Settings
from app.llm.ollama_provider import OllamaProvider
from app.llm.registry import UnsupportedProviderError, _build_provider_cached, get_llm_provider


class TestLLMRegistry(unittest.TestCase):
    def setUp(self) -> None:
        _build_provider_cached.cache_clear()

    def test_returns_ollama_provider_when_configured(self) -> None:
        settings = Settings(
            LLM_PROVIDER="ollama",
            OLLAMA_BASE_URL="http://localhost:11434",
            LLM_REQUEST_TIMEOUT_SECONDS=15,
        )

        provider = get_llm_provider(settings)

        self.assertIsInstance(provider, OllamaProvider)
        self.assertEqual(provider.provider_name, "ollama")

    def test_raises_for_unsupported_provider(self) -> None:
        settings = Settings(
            LLM_PROVIDER="not-real",
            OLLAMA_BASE_URL="http://localhost:11434",
            LLM_REQUEST_TIMEOUT_SECONDS=15,
        )

        with self.assertRaises(UnsupportedProviderError):
            get_llm_provider(settings)


if __name__ == "__main__":
    unittest.main()
