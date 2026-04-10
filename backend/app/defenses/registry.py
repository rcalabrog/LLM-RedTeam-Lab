from .base import DefenseModule
from .context_sanitizer import ContextSanitizerDefense
from .input_filter import InputFilterDefense
from .output_guard import OutputGuardDefense
from .schemas import DefenseDescriptor, DefenseStage

DEFAULT_GUARDED_DEFENSES: tuple[str, ...] = (
    "input_filter",
    "context_sanitizer",
    "output_guard",
)

_DEFENSE_ORDER: tuple[str, ...] = DEFAULT_GUARDED_DEFENSES

_DEFENSE_DESCRIPTIONS: dict[str, DefenseDescriptor] = {
    "input_filter": DefenseDescriptor(
        defense_name="input_filter",
        stage=DefenseStage.pre_input,
        description="Deterministic suspicious-pattern detection on raw user input.",
    ),
    "context_sanitizer": DefenseDescriptor(
        defense_name="context_sanitizer",
        stage=DefenseStage.context_sanitization,
        description="Reinforces instruction boundaries and sanitizes risky input fragments.",
    ),
    "output_guard": DefenseDescriptor(
        defense_name="output_guard",
        stage=DefenseStage.post_output,
        description="Detects prompt leakage/simulated secret leakage in model output.",
    ),
}


class DefenseRegistryError(ValueError):
    """Raised when a requested defense name is not available."""


def list_available_defenses() -> list[DefenseDescriptor]:
    return [_DEFENSE_DESCRIPTIONS[name] for name in _DEFENSE_ORDER]


def list_default_guarded_defenses() -> list[str]:
    return list(DEFAULT_GUARDED_DEFENSES)


def _instantiate_defense(name: str) -> DefenseModule:
    if name == "input_filter":
        return InputFilterDefense(block_high_risk=True)
    if name == "context_sanitizer":
        return ContextSanitizerDefense(reinforce_boundary=True)
    if name == "output_guard":
        return OutputGuardDefense(replace_unsafe_output=True)
    raise DefenseRegistryError(f"Unknown defense '{name}'.")


def resolve_defense_modules(enabled: list[str] | None = None) -> list[DefenseModule]:
    requested = enabled or list(DEFAULT_GUARDED_DEFENSES)
    normalized = [name.strip().lower() for name in requested if name.strip()]
    if not normalized:
        raise DefenseRegistryError("At least one defense must be enabled.")

    unknown = [name for name in normalized if name not in _DEFENSE_DESCRIPTIONS]
    if unknown:
        unknown_sorted = ", ".join(sorted(set(unknown)))
        raise DefenseRegistryError(f"Unknown defense(s): {unknown_sorted}.")

    allowed = set(normalized)
    ordered = [name for name in _DEFENSE_ORDER if name in allowed]
    return [_instantiate_defense(name) for name in ordered]
