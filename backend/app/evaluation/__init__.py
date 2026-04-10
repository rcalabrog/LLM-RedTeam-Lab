"""Deterministic campaign evaluation services and schemas."""

from .evaluator import CampaignEvaluator
from .metrics import build_campaign_metrics
from .schemas import (
    AttackEvaluationResult,
    CampaignEvaluationSummary,
    CategoryEvaluationBreakdown,
    EvaluatedCampaignResult,
    EvaluationClassification,
    EvaluationSignal,
    MatchedRule,
    SeverityEvaluationBreakdown,
)

__all__ = [
    "AttackEvaluationResult",
    "CampaignEvaluationSummary",
    "CampaignEvaluator",
    "CategoryEvaluationBreakdown",
    "EvaluatedCampaignResult",
    "EvaluationClassification",
    "EvaluationSignal",
    "MatchedRule",
    "SeverityEvaluationBreakdown",
    "build_campaign_metrics",
]
