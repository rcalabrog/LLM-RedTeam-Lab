from datetime import datetime, timezone

from pydantic import BaseModel, Field

from ..evaluation import EvaluatedCampaignResult
from ..orchestration import CampaignRunResult


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SaveEvaluatedCampaignRequest(BaseModel):
    """Payload used to persist one evaluated campaign run."""

    run_result: CampaignRunResult
    evaluated_result: EvaluatedCampaignResult


class SavedCampaignSummary(BaseModel):
    run_id: str
    campaign_name: str
    target_name: str
    pipeline_state: str
    completed_at: datetime
    evaluated_at: datetime
    total_attacks: int
    success_count: int
    failed_count: int
    ambiguous_count: int
    success_rate_overall: float


class SavedCampaignRecord(BaseModel):
    """Full persisted campaign including raw and evaluated layers."""

    saved_at: datetime = Field(default_factory=utcnow)
    run_result: CampaignRunResult
    evaluated_result: EvaluatedCampaignResult
