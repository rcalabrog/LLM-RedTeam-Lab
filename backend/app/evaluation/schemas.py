from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field

from ..attacks import AttackCategory, AttackSeverity
from ..orchestration import AttackExecutionStatus


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class EvaluationClassification(str, Enum):
    success = "success"
    failed = "failed"
    ambiguous = "ambiguous"


class EvaluationSignal(str, Enum):
    target_execution_error = "target_execution_error"
    explicit_refusal = "explicit_refusal"
    guarded_refusal = "guarded_refusal"
    suspicious_flagging = "suspicious_flagging"
    prompt_disclosure_indicator = "prompt_disclosure_indicator"
    policy_override_acceptance = "policy_override_acceptance"
    malicious_compliance_indicator = "malicious_compliance_indicator"
    simulated_secret_exposure = "simulated_secret_exposure"
    empty_response = "empty_response"
    mixed_signal_conflict = "mixed_signal_conflict"


class MatchedRule(BaseModel):
    rule_id: str
    signal: EvaluationSignal
    evidence: str


class AttackEvaluationResult(BaseModel):
    attack_id: str
    attack_name: str
    category: AttackCategory
    severity: AttackSeverity
    target_name: str
    classification: EvaluationClassification
    matched_signals: list[EvaluationSignal] = Field(default_factory=list)
    matched_rules: list[MatchedRule] = Field(default_factory=list)
    reasoning_summary: str
    response_excerpt: str | None = None
    source_execution_status: AttackExecutionStatus


class CategoryEvaluationBreakdown(BaseModel):
    category: AttackCategory
    total: int = Field(ge=0)
    success: int = Field(ge=0)
    failed: int = Field(ge=0)
    ambiguous: int = Field(ge=0)
    success_rate: float = Field(ge=0.0, le=1.0)


class SeverityEvaluationBreakdown(BaseModel):
    severity: AttackSeverity
    total: int = Field(ge=0)
    success: int = Field(ge=0)
    failed: int = Field(ge=0)
    ambiguous: int = Field(ge=0)
    success_rate: float = Field(ge=0.0, le=1.0)


class CampaignEvaluationSummary(BaseModel):
    total_attacks: int = Field(ge=0)
    success_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)
    ambiguous_count: int = Field(ge=0)
    success_rate_overall: float = Field(ge=0.0, le=1.0)
    failed_rate_overall: float = Field(ge=0.0, le=1.0)
    ambiguous_rate_overall: float = Field(ge=0.0, le=1.0)
    per_category: list[CategoryEvaluationBreakdown] = Field(default_factory=list)
    per_severity: list[SeverityEvaluationBreakdown] = Field(default_factory=list)


class EvaluatedCampaignResult(BaseModel):
    run_id: str
    campaign_name: str
    target_name: str
    evaluated_at: datetime = Field(default_factory=now_utc)
    source_started_at: datetime
    source_completed_at: datetime
    evaluations: list[AttackEvaluationResult] = Field(default_factory=list)
    summary: CampaignEvaluationSummary
