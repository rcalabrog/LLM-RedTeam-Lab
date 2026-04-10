from collections import defaultdict

from ..attacks import AttackCategory, AttackSeverity
from .schemas import (
    AttackEvaluationResult,
    CampaignEvaluationSummary,
    CategoryEvaluationBreakdown,
    EvaluationClassification,
    SeverityEvaluationBreakdown,
)


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def build_campaign_metrics(evaluations: list[AttackEvaluationResult]) -> CampaignEvaluationSummary:
    total = len(evaluations)
    success_count = sum(1 for item in evaluations if item.classification == EvaluationClassification.success)
    failed_count = sum(1 for item in evaluations if item.classification == EvaluationClassification.failed)
    ambiguous_count = sum(
        1 for item in evaluations if item.classification == EvaluationClassification.ambiguous
    )

    by_category: dict[
        AttackCategory,
        dict[EvaluationClassification, int],
    ] = defaultdict(lambda: defaultdict(int))
    by_severity: dict[
        AttackSeverity,
        dict[EvaluationClassification, int],
    ] = defaultdict(lambda: defaultdict(int))

    for item in evaluations:
        by_category[item.category][item.classification] += 1
        by_severity[item.severity][item.classification] += 1

    per_category = []
    for category in sorted(AttackCategory, key=lambda current: current.value):
        class_counts = by_category.get(category, {})
        category_total = sum(class_counts.values())
        category_success = class_counts.get(EvaluationClassification.success, 0)
        category_failed = class_counts.get(EvaluationClassification.failed, 0)
        category_ambiguous = class_counts.get(EvaluationClassification.ambiguous, 0)
        per_category.append(
            CategoryEvaluationBreakdown(
                category=category,
                total=category_total,
                success=category_success,
                failed=category_failed,
                ambiguous=category_ambiguous,
                success_rate=_rate(category_success, category_total),
            )
        )

    per_severity = []
    for severity in sorted(AttackSeverity, key=lambda current: current.value):
        class_counts = by_severity.get(severity, {})
        severity_total = sum(class_counts.values())
        severity_success = class_counts.get(EvaluationClassification.success, 0)
        severity_failed = class_counts.get(EvaluationClassification.failed, 0)
        severity_ambiguous = class_counts.get(EvaluationClassification.ambiguous, 0)
        per_severity.append(
            SeverityEvaluationBreakdown(
                severity=severity,
                total=severity_total,
                success=severity_success,
                failed=severity_failed,
                ambiguous=severity_ambiguous,
                success_rate=_rate(severity_success, severity_total),
            )
        )

    return CampaignEvaluationSummary(
        total_attacks=total,
        success_count=success_count,
        failed_count=failed_count,
        ambiguous_count=ambiguous_count,
        success_rate_overall=_rate(success_count, total),
        failed_rate_overall=_rate(failed_count, total),
        ambiguous_rate_overall=_rate(ambiguous_count, total),
        per_category=per_category,
        per_severity=per_severity,
    )
