from .base import DefenseModule
from .registry import resolve_defense_modules
from .schemas import (
    DefenseAction,
    DefenseEvent,
    DefenseInputPayload,
    DefenseOutputPayload,
    DefensePipelineSummary,
    DefenseRiskLevel,
    DefenseStage,
)

_RISK_RANK: dict[DefenseRiskLevel, int] = {
    DefenseRiskLevel.low: 1,
    DefenseRiskLevel.medium: 2,
    DefenseRiskLevel.high: 3,
}

_BLOCK_MESSAGE = (
    "I cannot help with requests to override instructions or reveal hidden prompts. "
    "Please provide a normal task and I can help with that."
)


def _max_risk(current: DefenseRiskLevel, new: DefenseRiskLevel) -> DefenseRiskLevel:
    return new if _RISK_RANK[new] > _RISK_RANK[current] else current


class DefensePipeline:
    """Deterministic multi-stage defense pipeline."""

    def __init__(self, enabled_defenses: list[str] | None = None) -> None:
        self._modules: list[DefenseModule] = resolve_defense_modules(enabled_defenses)
        self.enabled_defenses = [module.defense_name for module in self._modules]

    def run_pre_llm(self, payload: DefenseInputPayload) -> tuple[DefenseInputPayload, DefensePipelineSummary]:
        current = payload.model_copy(deep=True)
        summary = DefensePipelineSummary(
            enabled_defenses=self.enabled_defenses,
            final_user_input=current.user_input,
            final_system_prompt=current.system_prompt,
        )

        for module in self._modules:
            if module.stage not in (DefenseStage.pre_input, DefenseStage.context_sanitization):
                continue

            event = module.apply_input(current)
            self._apply_event_to_summary(summary, event)

            if event.modified_input is not None:
                current.user_input = event.modified_input
            if event.modified_system_prompt is not None:
                current.system_prompt = event.modified_system_prompt

            summary.final_user_input = current.user_input
            summary.final_system_prompt = current.system_prompt

            if event.blocked:
                summary.blocked = True
                summary.block_message = _BLOCK_MESSAGE
                break

        return current, summary

    def run_post_llm(
        self,
        input_payload: DefenseInputPayload,
        response_text: str,
        existing_summary: DefensePipelineSummary,
    ) -> tuple[str, DefensePipelineSummary]:
        current_output = response_text
        summary = existing_summary.model_copy(deep=True)

        for module in self._modules:
            if module.stage != DefenseStage.post_output:
                continue

            event = module.apply_output(
                DefenseOutputPayload(
                    response_text=current_output,
                    input_payload=input_payload,
                    metadata={"enabled_defenses": self.enabled_defenses},
                )
            )
            self._apply_event_to_summary(summary, event)
            if event.modified_output is not None:
                current_output = event.modified_output

        summary.final_output = current_output
        return current_output, summary

    @staticmethod
    def _apply_event_to_summary(summary: DefensePipelineSummary, event: DefenseEvent) -> None:
        summary.events.append(event)
        summary.warnings.extend(event.warnings)
        summary.flags.extend(event.flags)
        summary.highest_risk_level = _max_risk(summary.highest_risk_level, event.risk_level)

        if event.action_taken == DefenseAction.blocked:
            summary.blocked = True
