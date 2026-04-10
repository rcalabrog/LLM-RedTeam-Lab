from typing import Any, Mapping

import httpx

from .base import (
    LLMProvider,
    LLMProviderConnectionError,
    LLMProviderResponseError,
    LLMProviderTimeoutError,
)
from .schemas import GenerationRequest, GenerationResponse, ProviderHealth


def normalize_ollama_generate_response(
    payload: Mapping[str, Any], *, fallback_model: str
) -> GenerationResponse:
    """Normalize Ollama's /api/generate response into provider-generic schema."""

    raw_model = payload.get("model")
    raw_content = payload.get("response")

    if not isinstance(raw_content, str):
        raise LLMProviderResponseError("Ollama response did not include a text 'response' field.")

    model = raw_model if isinstance(raw_model, str) and raw_model else fallback_model

    usage: dict[str, Any] = {}
    prompt_eval_count = payload.get("prompt_eval_count")
    eval_count = payload.get("eval_count")
    if isinstance(prompt_eval_count, int):
        usage["input_tokens"] = prompt_eval_count
    if isinstance(eval_count, int):
        usage["output_tokens"] = eval_count
    if isinstance(prompt_eval_count, int) and isinstance(eval_count, int):
        usage["total_tokens"] = prompt_eval_count + eval_count

    metadata: dict[str, Any] = {}
    for key in (
        "created_at",
        "done",
        "done_reason",
        "total_duration",
        "load_duration",
        "prompt_eval_duration",
        "eval_duration",
    ):
        value = payload.get(key)
        if value is not None:
            metadata[key] = value

    return GenerationResponse(
        model=model,
        content=raw_content,
        metadata=metadata,
        usage=usage,
    )


class OllamaProvider(LLMProvider):
    provider_name = "ollama"

    def __init__(self, *, base_url: str, timeout_seconds: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        payload: dict[str, Any] = {
            "model": request.model,
            "prompt": request.prompt,
            "stream": False,
        }

        if request.system_prompt:
            payload["system"] = request.system_prompt

        options: dict[str, Any] = {}
        if request.temperature is not None:
            options["temperature"] = request.temperature
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        if options:
            payload["options"] = options

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(f"{self._base_url}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise LLMProviderTimeoutError("Timed out while waiting for Ollama generate response.") from exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            body = exc.response.text[:300]
            raise LLMProviderResponseError(f"Ollama returned HTTP {status}: {body}") from exc
        except httpx.RequestError as exc:
            raise LLMProviderConnectionError(f"Failed to reach Ollama at {self._base_url}.") from exc
        except ValueError as exc:
            raise LLMProviderResponseError("Ollama returned non-JSON response content.") from exc

        return normalize_ollama_generate_response(data, fallback_model=request.model)

    async def health_check(self) -> ProviderHealth:
        endpoint = f"{self._base_url}/api/tags"

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.get(endpoint)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException:
            return ProviderHealth(
                provider=self.provider_name,
                available=False,
                status="unavailable",
                error="Timed out while checking Ollama availability.",
            )
        except httpx.HTTPStatusError as exc:
            return ProviderHealth(
                provider=self.provider_name,
                available=False,
                status="unavailable",
                error=f"Ollama health check returned HTTP {exc.response.status_code}.",
            )
        except httpx.RequestError:
            return ProviderHealth(
                provider=self.provider_name,
                available=False,
                status="unavailable",
                error=f"Unable to reach Ollama at {self._base_url}.",
            )
        except ValueError:
            return ProviderHealth(
                provider=self.provider_name,
                available=False,
                status="unavailable",
                error="Ollama health endpoint returned invalid JSON.",
            )

        models = data.get("models", [])
        model_count = len(models) if isinstance(models, list) else None
        metadata = {"base_url": self._base_url}
        if model_count is not None:
            metadata["model_count"] = model_count

        return ProviderHealth(
            provider=self.provider_name,
            available=True,
            status="ok",
            metadata=metadata,
        )
