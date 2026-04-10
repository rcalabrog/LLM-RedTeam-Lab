from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GenerationRequest(BaseModel):
    """Provider-agnostic generation request."""

    prompt: str = Field(min_length=1)
    model: str = Field(min_length=1)
    system_prompt: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, gt=0)


class GenerationResponse(BaseModel):
    """Normalized generation output across providers."""

    model: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    usage: dict[str, Any] = Field(default_factory=dict)


class ProviderHealth(BaseModel):
    """Generic provider health information."""

    model_config = ConfigDict(extra="ignore")

    provider: str
    available: bool
    status: str
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
