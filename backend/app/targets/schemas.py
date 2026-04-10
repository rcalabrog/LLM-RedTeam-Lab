from typing import Any

from pydantic import BaseModel, Field


class TargetInvocationRequest(BaseModel):
    """Request contract for invoking a target application."""

    user_input: str = Field(min_length=1)
    system_prompt_override: str | None = None
    model_override: str | None = None
    enabled_defenses: list[str] | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TargetExecutionMetadata(BaseModel):
    """Execution details that help inspect target behavior."""

    final_prompt_summary: str
    llm_called: bool
    prompt_source: str
    risk_level: str | None = None


class TargetInvocationResponse(BaseModel):
    """Normalized target response for lab orchestration and debugging."""

    target_name: str
    target_mode: str
    defense_mode: str
    model: str
    response_text: str
    warnings: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    execution: TargetExecutionMetadata
    metadata: dict[str, Any] = Field(default_factory=dict)


class TargetDescriptor(BaseModel):
    """High-level metadata for discoverable target types."""

    name: str
    mode: str
    defense_mode: str
    description: str
