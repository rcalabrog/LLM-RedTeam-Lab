from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from ..attacks import AttackCategory, AttackSeverity


def generate_run_id() -> str:
    return f"run_{uuid4().hex[:12]}"


class PipelineState(str, Enum):
    starting = "starting"
    running = "running"
    completed = "completed"
    completed_with_errors = "completed_with_errors"
    failed = "failed"


class AttackExecutionStatus(str, Enum):
    succeeded = "succeeded"
    failed = "failed"


class CampaignRunRequest(BaseModel):
    """Structured campaign request for batch attack execution."""

    campaign_name: str | None = None
    target_name: str = Field(min_length=3)
    attack_ids: list[str] = Field(default_factory=list)
    category: AttackCategory | None = None
    severity: AttackSeverity | None = None
    model_override: str | None = None
    system_prompt_override: str | None = None
    enabled_defenses: list[str] | None = None
    max_attacks: int | None = Field(default=None, gt=0)
    stop_on_error: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttackExecutionMetadataSnapshot(BaseModel):
    """Execution metadata captured from target invocation without evaluation."""

    final_prompt_summary: str | None = None
    risk_level: str | None = None
    llm_called: bool | None = None
    prompt_source: str | None = None
    target_mode: str | None = None
    raw_target_metadata: dict[str, Any] = Field(default_factory=dict)


class CampaignAttackResult(BaseModel):
    """Raw execution result for one attack prompt against one target."""

    attack_id: str
    attack_name: str
    category: AttackCategory
    severity: AttackSeverity
    target_name: str
    target_name_snapshot: str | None = None
    defense_mode: str | None = None
    attack_prompt_snapshot: str | None = None
    attack_description_snapshot: str | None = None
    model: str
    response_text: str
    warnings: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    execution_metadata: AttackExecutionMetadataSnapshot = Field(
        default_factory=AttackExecutionMetadataSnapshot
    )
    execution_status: AttackExecutionStatus
    error_message: str | None = None
    started_at: datetime
    completed_at: datetime


class CampaignAggregateCounts(BaseModel):
    selected_attacks: int = Field(ge=0)
    executed_attacks: int = Field(ge=0)
    succeeded_attacks: int = Field(ge=0)
    failed_attacks: int = Field(ge=0)


class CampaignRunResult(BaseModel):
    """Top-level campaign execution result."""

    run_id: str = Field(default_factory=generate_run_id)
    campaign_name: str
    state: PipelineState
    target_name: str
    category_filter: AttackCategory | None = None
    severity_filter: AttackSeverity | None = None
    attack_ids_filter: list[str] = Field(default_factory=list)
    stop_on_error: bool
    model_override: str | None = None
    enabled_defenses: list[str] | None = None
    system_prompt_override_used: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime
    completed_at: datetime
    counts: CampaignAggregateCounts
    results: list[CampaignAttackResult] = Field(default_factory=list)


class AttackSelectionPreview(BaseModel):
    selected_attack_ids: list[str]
    selected_count: int = Field(ge=0)
    category_filter: AttackCategory | None = None
    severity_filter: AttackSeverity | None = None
