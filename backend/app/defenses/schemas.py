from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DefenseStage(str, Enum):
    pre_input = "pre_input"
    context_sanitization = "context_sanitization"
    post_output = "post_output"


class DefenseAction(str, Enum):
    pass_through = "pass_through"
    flagged = "flagged"
    modified = "modified"
    blocked = "blocked"
    replaced_output = "replaced_output"


class DefenseRiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class DefenseEvent(BaseModel):
    """Single defense decision emitted by one defense module."""

    defense_name: str
    stage: DefenseStage
    action_taken: DefenseAction
    warnings: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    risk_level: DefenseRiskLevel = DefenseRiskLevel.low
    blocked: bool = False
    modified_input: str | None = None
    modified_system_prompt: str | None = None
    modified_output: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DefenseInputPayload(BaseModel):
    """Payload exposed to input/context defenses."""

    user_input: str
    system_prompt: str
    model: str
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DefenseOutputPayload(BaseModel):
    """Payload exposed to post-output defenses."""

    response_text: str
    input_payload: DefenseInputPayload
    metadata: dict[str, Any] = Field(default_factory=dict)


class DefensePipelineSummary(BaseModel):
    """Aggregate defense trace for one target invocation."""

    enabled_defenses: list[str]
    events: list[DefenseEvent] = Field(default_factory=list)
    blocked: bool = False
    warnings: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    highest_risk_level: DefenseRiskLevel = DefenseRiskLevel.low
    final_user_input: str
    final_system_prompt: str
    final_output: str | None = None
    block_message: str | None = None


class DefenseDescriptor(BaseModel):
    defense_name: str
    stage: DefenseStage
    description: str
