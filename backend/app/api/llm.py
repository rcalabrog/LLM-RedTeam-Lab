from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..core.config import Settings, get_settings
from ..llm import (
    GenerationRequest,
    GenerationResponse,
    LLMProvider,
    LLMProviderError,
    get_llm_provider,
)

router = APIRouter(prefix="/llm", tags=["llm"])


class LLMIntegrationCheckResponse(BaseModel):
    provider: str
    model: str
    status: str
    output: GenerationResponse


async def _run_connectivity_prompt(
    provider: LLMProvider, settings: Settings
) -> GenerationResponse:
    request = GenerationRequest(
        prompt="Reply with exactly: LLM Red Team Lab connectivity check.",
        model=settings.default_main_model,
        system_prompt="You are a concise assistant used for local connectivity checks.",
        temperature=settings.llm_generation_temperature,
        max_tokens=settings.llm_generation_max_tokens,
    )
    return await provider.generate(request)


@router.post(
    "/test",
    response_model=LLMIntegrationCheckResponse,
    summary="Run a safe LLM integration check using the configured main model",
)
async def llm_integration_check(
    settings: Settings = Depends(get_settings),
) -> LLMIntegrationCheckResponse:
    provider = get_llm_provider(settings)
    try:
        output = await _run_connectivity_prompt(provider, settings)
    except LLMProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return LLMIntegrationCheckResponse(
        provider=provider.provider_name,
        model=settings.default_main_model,
        status="ok",
        output=output,
    )
