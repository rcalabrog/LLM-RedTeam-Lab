from collections.abc import Callable
from datetime import datetime, timezone

from ..attacks import AttackDefinition, AttackLibrary
from ..core.config import Settings
from ..targets import (
    TargetApp,
    TargetInvocationRequest,
    TargetNotFoundError,
    get_target,
)
from .schemas import (
    AttackExecutionStatus,
    AttackExecutionMetadataSnapshot,
    CampaignAggregateCounts,
    CampaignAttackResult,
    CampaignRunRequest,
    CampaignRunResult,
    PipelineState,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CampaignRequestError(ValueError):
    """Raised when campaign request parameters produce an invalid run."""


class CampaignTargetResolutionError(RuntimeError):
    """Raised when the configured target cannot be resolved."""


class CampaignRunner:
    """Executes attack batches against a selected target app."""

    def __init__(
        self,
        *,
        attack_library: AttackLibrary | None = None,
        target_resolver: Callable[[str, Settings], TargetApp] = get_target,
    ) -> None:
        self._attack_library = attack_library or AttackLibrary()
        self._target_resolver = target_resolver

    def select_attacks(self, request: CampaignRunRequest) -> list[AttackDefinition]:
        """Resolve attacks using deterministic intersection semantics."""
        attacks = self._attack_library.get_all_attacks()
        by_id = {attack.attack_id: attack for attack in attacks}

        if request.attack_ids:
            requested_unique_ids = list(dict.fromkeys(request.attack_ids))
            missing_ids = [attack_id for attack_id in requested_unique_ids if attack_id not in by_id]
            if missing_ids:
                raise CampaignRequestError(
                    f"Unknown attack_id values: {', '.join(sorted(missing_ids))}."
                )
            allowed = set(requested_unique_ids)
            attacks = [attack for attack in attacks if attack.attack_id in allowed]

        if request.category is not None:
            attacks = [attack for attack in attacks if attack.category == request.category]

        if request.severity is not None:
            attacks = [attack for attack in attacks if attack.severity == request.severity]

        if request.max_attacks is not None:
            attacks = attacks[: request.max_attacks]

        if not attacks:
            raise CampaignRequestError(
                "No attacks selected. Adjust filters, max_attacks, or attack_ids."
            )

        return attacks

    def preview_selection(self, request: CampaignRunRequest) -> list[AttackDefinition]:
        return self.select_attacks(request)

    async def execute(self, request: CampaignRunRequest, settings: Settings) -> CampaignRunResult:
        started_at = utcnow()
        campaign_name = request.campaign_name or f"{request.target_name}_campaign"
        selected_attacks = self.select_attacks(request)

        try:
            target = self._target_resolver(request.target_name, settings)
        except TargetNotFoundError as exc:
            raise CampaignTargetResolutionError(str(exc)) from exc
        except Exception as exc:
            raise CampaignTargetResolutionError(
                f"Failed to resolve target '{request.target_name}': {exc}"
            ) from exc

        results: list[CampaignAttackResult] = []
        state = PipelineState.running

        for attack in selected_attacks:
            attack_started_at = utcnow()
            try:
                target_response = await target.invoke(
                    TargetInvocationRequest(
                        user_input=attack.prompt,
                        system_prompt_override=request.system_prompt_override,
                        model_override=request.model_override,
                        enabled_defenses=request.enabled_defenses,
                        tags=[
                            "campaign_run",
                            "attack_library",
                            f"category:{attack.category.value}",
                        ],
                        metadata={
                            "campaign_name": campaign_name,
                            "attack_id": attack.attack_id,
                            "attack_name": attack.name,
                            "attack_category": attack.category.value,
                            "attack_severity": attack.severity.value,
                            "campaign_metadata": request.metadata,
                        },
                    )
                )

                results.append(
                    CampaignAttackResult(
                        attack_id=attack.attack_id,
                        attack_name=attack.name,
                        category=attack.category,
                        severity=attack.severity,
                        target_name=request.target_name,
                        target_name_snapshot=target_response.target_name,
                        defense_mode=target_response.defense_mode,
                        attack_prompt_snapshot=attack.prompt,
                        attack_description_snapshot=attack.description,
                        model=target_response.model,
                        response_text=target_response.response_text,
                        warnings=target_response.warnings,
                        flags=target_response.flags,
                        execution_metadata=AttackExecutionMetadataSnapshot(
                            final_prompt_summary=target_response.execution.final_prompt_summary,
                            risk_level=target_response.execution.risk_level,
                            llm_called=target_response.execution.llm_called,
                            prompt_source=target_response.execution.prompt_source,
                            target_mode=target_response.target_mode,
                            raw_target_metadata=target_response.metadata,
                        ),
                        execution_status=AttackExecutionStatus.succeeded,
                        started_at=attack_started_at,
                        completed_at=utcnow(),
                    )
                )
            except Exception as exc:
                results.append(
                    CampaignAttackResult(
                        attack_id=attack.attack_id,
                        attack_name=attack.name,
                        category=attack.category,
                        severity=attack.severity,
                        target_name=request.target_name,
                        target_name_snapshot=request.target_name,
                        defense_mode=None,
                        attack_prompt_snapshot=attack.prompt,
                        attack_description_snapshot=attack.description,
                        model=request.model_override or settings.default_main_model,
                        response_text="",
                        warnings=[],
                        flags=[],
                        execution_metadata=AttackExecutionMetadataSnapshot(
                            llm_called=None,
                        ),
                        execution_status=AttackExecutionStatus.failed,
                        error_message=str(exc),
                        started_at=attack_started_at,
                        completed_at=utcnow(),
                    )
                )
                if request.stop_on_error:
                    break

        succeeded = sum(
            1 for result in results if result.execution_status == AttackExecutionStatus.succeeded
        )
        failed = sum(1 for result in results if result.execution_status == AttackExecutionStatus.failed)

        if failed == 0:
            state = PipelineState.completed
        elif succeeded == 0:
            state = PipelineState.failed
        else:
            state = PipelineState.completed_with_errors

        completed_at = utcnow()
        counts = CampaignAggregateCounts(
            selected_attacks=len(selected_attacks),
            executed_attacks=len(results),
            succeeded_attacks=succeeded,
            failed_attacks=failed,
        )

        return CampaignRunResult(
            campaign_name=campaign_name,
            state=state,
            target_name=request.target_name,
            category_filter=request.category,
            severity_filter=request.severity,
            attack_ids_filter=list(dict.fromkeys(request.attack_ids)),
            stop_on_error=request.stop_on_error,
            model_override=request.model_override,
            enabled_defenses=request.enabled_defenses,
            system_prompt_override_used=request.system_prompt_override is not None,
            metadata=request.metadata,
            started_at=started_at,
            completed_at=completed_at,
            counts=counts,
            results=results,
        )
