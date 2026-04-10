import unittest

from app.llm.base import LLMProviderResponseError
from app.llm.ollama_provider import normalize_ollama_generate_response


class TestOllamaNormalization(unittest.TestCase):
    def test_normalizes_generate_response(self) -> None:
        payload = {
            "model": "qwen3.5:9b",
            "response": "LLM Red Team Lab connectivity check.",
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": 7,
            "eval_count": 9,
            "total_duration": 123456,
        }

        normalized = normalize_ollama_generate_response(payload, fallback_model="fallback-model")

        self.assertEqual(normalized.model, "qwen3.5:9b")
        self.assertEqual(normalized.content, "LLM Red Team Lab connectivity check.")
        self.assertEqual(normalized.usage["input_tokens"], 7)
        self.assertEqual(normalized.usage["output_tokens"], 9)
        self.assertEqual(normalized.usage["total_tokens"], 16)
        self.assertEqual(normalized.metadata["done_reason"], "stop")

    def test_uses_fallback_model_when_missing(self) -> None:
        payload = {"response": "ok", "done": True}

        normalized = normalize_ollama_generate_response(payload, fallback_model="fallback-model")

        self.assertEqual(normalized.model, "fallback-model")
        self.assertEqual(normalized.content, "ok")

    def test_raises_when_response_text_missing(self) -> None:
        payload = {"model": "qwen3.5:9b", "done": True}

        with self.assertRaises(LLMProviderResponseError):
            normalize_ollama_generate_response(payload, fallback_model="fallback-model")


if __name__ == "__main__":
    unittest.main()
