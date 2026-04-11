from ..llm import GenerationRequest, LLMProvider
from ..prompts.loader import load_prompt_template
from .base import TargetApp
from .schemas import TargetExecutionMetadata, TargetInvocationRequest, TargetInvocationResponse


class SimpleVulnerableChatTarget(TargetApp):
    """
    Intentionally vulnerable chat target for red-team exercises.

    This target keeps prompt assembly naive on purpose so prompt-injection and
    extraction techniques remain visible in later phases of the lab.
    """

    target_name = "simple_vulnerable_chat"
    target_mode = "vulnerable"
    defense_mode = "none"
    description = "Naive chat target with minimal hardening."

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
        self._base_system_prompt = load_prompt_template(
            "targets/simple_vulnerable_chat_system.txt"
        )

    async def invoke(self, request: TargetInvocationRequest) -> TargetInvocationResponse:
        model = request.model_override or self._default_model
        system_prompt = request.system_prompt_override or self._base_system_prompt
        prompt_source = "override" if request.system_prompt_override else "default_template"

        llm_response = await self._provider.generate(
            GenerationRequest(
                prompt=request.user_input,
                model=model,
                system_prompt=system_prompt,
                temperature=self._generation_temperature,
                max_tokens=self._generation_max_tokens,
            )
        )

        return TargetInvocationResponse(
            target_name=self.target_name,
            target_mode=self.target_mode,
            defense_mode=self.defense_mode,
            model=llm_response.model,
            response_text=llm_response.content,
            warnings=["Intentionally vulnerable target: minimal prompt hardening enabled."],
            flags=[],
            execution=TargetExecutionMetadata(
                final_prompt_summary="System prompt + raw user input sent directly to the model.",
                llm_called=True,
                prompt_source=prompt_source,
                risk_level="high",
            ),
            metadata={
                "request_tags": request.tags,
                "request_metadata": request.metadata,
                "system_prompt_used": system_prompt,
                "provider_metadata": llm_response.metadata,
                "usage": llm_response.usage,
            },
        )
