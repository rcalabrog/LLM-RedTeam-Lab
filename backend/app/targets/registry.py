from ..core.config import Settings
from ..llm import get_llm_provider
from .base import TargetApp, TargetNotFoundError
from .guarded_chat_target import GuardedChatTarget
from .schemas import TargetDescriptor
from .simple_chat_target import SimpleVulnerableChatTarget


_TARGET_DESCRIPTORS: tuple[TargetDescriptor, ...] = (
    TargetDescriptor(
        name="simple_vulnerable_chat",
        mode="vulnerable",
        defense_mode="none",
        description="Naive chat target with minimal hardening.",
    ),
    TargetDescriptor(
        name="guarded_chat",
        mode="guarded",
        defense_mode="basic_guardrails",
        description="Chat target with deterministic suspicious-input checks.",
    ),
)


def list_available_targets() -> list[TargetDescriptor]:
    return list(_TARGET_DESCRIPTORS)


def get_target(name: str, settings: Settings) -> TargetApp:
    normalized = name.strip().lower()
    provider = get_llm_provider(settings)

    if normalized == "simple_vulnerable_chat":
        return SimpleVulnerableChatTarget(
            provider=provider,
            default_model=settings.default_main_model,
            generation_temperature=settings.llm_generation_temperature,
            generation_max_tokens=settings.llm_generation_max_tokens,
        )

    if normalized == "guarded_chat":
        return GuardedChatTarget(
            provider=provider,
            default_model=settings.default_main_model,
            generation_temperature=settings.llm_generation_temperature,
            generation_max_tokens=settings.llm_generation_max_tokens,
        )

    raise TargetNotFoundError(f"Unknown target '{name}'.")


def get_default_target(settings: Settings) -> TargetApp:
    return get_target(settings.default_target, settings)
