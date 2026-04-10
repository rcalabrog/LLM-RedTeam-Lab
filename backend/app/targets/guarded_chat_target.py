from ..defenses import DefensePipeline, DefenseRiskLevel
from ..defenses.schemas import DefenseInputPayload
from ..llm import GenerationRequest, LLMProvider
from ..prompts.loader import load_prompt_template
from .base import TargetApp
from .schemas import TargetExecutionMetadata, TargetInvocationRequest, TargetInvocationResponse


class GuardedChatTarget(TargetApp):
    """Guarded target that applies a reusable deterministic defense pipeline."""

    target_name = "guarded_chat"
    target_mode = "guarded"
    defense_mode = "basic_guardrails"
    description = "Chat target with reusable deterministic defenses."

    def __init__(
        self,
        *,
        provider: LLMProvider,
        default_model: str,
        generation_temperature: float = 0.0,
        generation_max_tokens: int = 384,
    ) -> None:
        self._provider = provider
        self._default_model = default_model
        self._generation_temperature = generation_temperature
        self._generation_max_tokens = generation_max_tokens
        self._base_system_prompt = load_prompt_template("targets/guarded_chat_system.txt")

    async def invoke(self, request: TargetInvocationRequest) -> TargetInvocationResponse:
        model = request.model_override or self._default_model
        prompt_source = "override" if request.system_prompt_override else "default_template"
        system_prompt = request.system_prompt_override or self._base_system_prompt

        pipeline = DefensePipeline(enabled_defenses=request.enabled_defenses)
        pre_payload = DefenseInputPayload(
            user_input=request.user_input,
            system_prompt=system_prompt,
            model=model,
            tags=request.tags,
            metadata=request.metadata,
        )

        sanitized_payload, defense_summary = pipeline.run_pre_llm(pre_payload)
        if defense_summary.blocked:
            response_text = defense_summary.block_message or (
                "I cannot help with this request due to active safety guardrails."
            )
            return TargetInvocationResponse(
                target_name=self.target_name,
                target_mode=self.target_mode,
                defense_mode=self.defense_mode,
                model=model,
                response_text=response_text,
                warnings=defense_summary.warnings,
                flags=defense_summary.flags,
                execution=TargetExecutionMetadata(
                    final_prompt_summary="Request blocked by pre-LLM defense pipeline.",
                    llm_called=False,
                    prompt_source=prompt_source,
                    risk_level=defense_summary.highest_risk_level.value,
                ),
                metadata={
                    "request_tags": request.tags,
                    "request_metadata": request.metadata,
                    "refused": True,
                    "enabled_defenses": defense_summary.enabled_defenses,
                    "defense_summary": defense_summary.model_dump(),
                },
            )

        llm_response = await self._provider.generate(
            GenerationRequest(
                prompt=sanitized_payload.user_input,
                model=model,
                system_prompt=sanitized_payload.system_prompt,
                temperature=self._generation_temperature,
                max_tokens=self._generation_max_tokens,
            )
        )

        final_output, defense_summary = pipeline.run_post_llm(
            sanitized_payload,
            llm_response.content,
            defense_summary,
        )

        risk_level = defense_summary.highest_risk_level
        if risk_level == DefenseRiskLevel.low and defense_summary.flags:
            risk_level = DefenseRiskLevel.medium

        return TargetInvocationResponse(
            target_name=self.target_name,
            target_mode=self.target_mode,
            defense_mode=self.defense_mode,
            model=llm_response.model,
            response_text=final_output,
            warnings=defense_summary.warnings,
            flags=defense_summary.flags,
            execution=TargetExecutionMetadata(
                final_prompt_summary=(
                    "Applied reusable defense pipeline (input filter, context sanitizer, output guard)."
                ),
                llm_called=True,
                prompt_source=prompt_source,
                risk_level=risk_level.value,
            ),
            metadata={
                "request_tags": request.tags,
                "request_metadata": request.metadata,
                "provider_metadata": llm_response.metadata,
                "usage": llm_response.usage,
                "refused": False,
                "enabled_defenses": defense_summary.enabled_defenses,
                "sanitized_user_input": sanitized_payload.user_input,
                "sanitized_system_prompt": sanitized_payload.system_prompt,
                "defense_summary": defense_summary.model_dump(),
            },
        )
