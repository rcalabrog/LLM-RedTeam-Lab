import re

from .base import DefenseModule
from .schemas import (
    DefenseAction,
    DefenseEvent,
    DefenseInputPayload,
    DefenseOutputPayload,
    DefenseRiskLevel,
    DefenseStage,
)

_HIGH_RISK_PATTERNS: tuple[tuple[str, str], ...] = (
    (
        "prompt_injection_override",
        r"\b(ignore|disregard)\b.{0,40}\b(previous|prior|system|developer)\b.{0,40}\b(instruction|prompt)s?\b",
    ),
    (
        "system_prompt_exfiltration",
        r"\b(reveal|show|print|leak)\b.{0,60}\b(system prompt|developer prompt|hidden instruction)s?\b",
    ),
    ("jailbreak_attempt", r"\b(jailbreak|do anything now|dan)\b"),
)

_MEDIUM_RISK_PATTERNS: tuple[tuple[str, str], ...] = (
    ("role_override_attempt", r"\b(you are now|pretend to be|act as)\b"),
    ("safety_bypass_attempt", r"\b(bypass|override|disable)\b.{0,30}\b(safety|guard|policy)\b"),
    ("sensitive_instruction_request", r"\b(internal rules|hidden rules|secret prompt)\b"),
)


def inspect_suspicious_input(user_input: str) -> tuple[list[str], DefenseRiskLevel, bool]:
    lowered = user_input.lower()
    flags: list[str] = []

    for flag_name, pattern in _HIGH_RISK_PATTERNS:
        if re.search(pattern, lowered):
            flags.append(flag_name)
    for flag_name, pattern in _MEDIUM_RISK_PATTERNS:
        if re.search(pattern, lowered):
            flags.append(flag_name)

    unique_flags = sorted(set(flags))
    blocked = any(flag in unique_flags for flag, _ in _HIGH_RISK_PATTERNS)
    risk = (
        DefenseRiskLevel.high
        if blocked
        else (DefenseRiskLevel.medium if unique_flags else DefenseRiskLevel.low)
    )
    return unique_flags, risk, blocked


class InputFilterDefense(DefenseModule):
    defense_name = "input_filter"
    stage = DefenseStage.pre_input

    def __init__(self, *, block_high_risk: bool = True) -> None:
        self._block_high_risk = block_high_risk

    def apply_input(self, payload: DefenseInputPayload) -> DefenseEvent:
        flags, risk, should_block = inspect_suspicious_input(payload.user_input)
        warnings: list[str] = []

        if flags:
            warnings.append("Suspicious prompt patterns detected in user input.")
        blocked = bool(should_block and self._block_high_risk)
        action = (
            DefenseAction.blocked
            if blocked
            else (DefenseAction.flagged if flags else DefenseAction.pass_through)
        )
        if blocked:
            warnings.append("Input blocked by input_filter due to high-risk patterns.")

        return DefenseEvent(
            defense_name=self.defense_name,
            stage=self.stage,
            action_taken=action,
            warnings=warnings,
            flags=flags,
            risk_level=risk,
            blocked=blocked,
            metadata={"block_high_risk": self._block_high_risk},
        )

    def apply_output(self, payload: DefenseOutputPayload) -> DefenseEvent:
        return DefenseEvent(
            defense_name=self.defense_name,
            stage=DefenseStage.post_output,
            action_taken=DefenseAction.pass_through,
            risk_level=DefenseRiskLevel.low,
        )
