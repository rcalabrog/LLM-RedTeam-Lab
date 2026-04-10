from ..orchestration import CampaignRunResult
from .metrics import build_campaign_metrics
from .rules import evaluate_attack_rules
from .schemas import AttackEvaluationResult, EvaluatedCampaignResult


class CampaignEvaluator:
    """Deterministic campaign evaluator using explicit rule checks."""

    def evaluate_campaign(self, campaign: CampaignRunResult) -> EvaluatedCampaignResult:
        evaluations: list[AttackEvaluationResult] = []

        for attack_result in campaign.results:
            (
                classification,
                matched_signals,
                matched_rules,
                reasoning_summary,
                response_excerpt,
            ) = evaluate_attack_rules(attack_result)

            evaluations.append(
                AttackEvaluationResult(
                    attack_id=attack_result.attack_id,
                    attack_name=attack_result.attack_name,
                    category=attack_result.category,
                    severity=attack_result.severity,
                    target_name=attack_result.target_name,
                    classification=classification,
                    matched_signals=matched_signals,
                    matched_rules=matched_rules,
                    reasoning_summary=reasoning_summary,
                    response_excerpt=response_excerpt,
                    source_execution_status=attack_result.execution_status,
                )
            )

        return EvaluatedCampaignResult(
            run_id=campaign.run_id,
            campaign_name=campaign.campaign_name,
            target_name=campaign.target_name,
            source_started_at=campaign.started_at,
            source_completed_at=campaign.completed_at,
            evaluations=evaluations,
            summary=build_campaign_metrics(evaluations),
        )
