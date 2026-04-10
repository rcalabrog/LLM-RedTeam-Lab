from collections import Counter
from typing import Iterable

from .data_leakage import DATA_LEAKAGE_SIMULATION_ATTACKS
from .exfiltration import SYSTEM_PROMPT_EXTRACTION_ATTACKS
from .jailbreaks import JAILBREAK_ATTACKS
from .policy_bypass import POLICY_BYPASS_ATTACKS
from .prompt_injection import PROMPT_INJECTION_ATTACKS
from .schemas import AttackCategory, AttackCategoryCount, AttackDefinition, AttackSeverity


def load_builtin_attacks() -> tuple[AttackDefinition, ...]:
    """Load all built-in static attack definitions."""
    return (
        *JAILBREAK_ATTACKS,
        *PROMPT_INJECTION_ATTACKS,
        *SYSTEM_PROMPT_EXTRACTION_ATTACKS,
        *POLICY_BYPASS_ATTACKS,
        *DATA_LEAKAGE_SIMULATION_ATTACKS,
    )


class AttackCatalog:
    """In-memory catalog for static attack definitions."""

    def __init__(self, attacks: Iterable[AttackDefinition] | None = None) -> None:
        self._attacks = tuple(attacks if attacks is not None else load_builtin_attacks())
        self._by_id: dict[str, AttackDefinition] = {}

        for attack in self._attacks:
            if attack.attack_id in self._by_id:
                raise ValueError(f"Duplicate attack_id detected: {attack.attack_id}")
            self._by_id[attack.attack_id] = attack

    def all(self) -> list[AttackDefinition]:
        return list(self._attacks)

    def get(self, attack_id: str) -> AttackDefinition | None:
        return self._by_id.get(attack_id)

    def filter(
        self,
        *,
        category: AttackCategory | None = None,
        severity: AttackSeverity | None = None,
    ) -> list[AttackDefinition]:
        filtered = self._attacks
        if category is not None:
            filtered = tuple(attack for attack in filtered if attack.category == category)
        if severity is not None:
            filtered = tuple(attack for attack in filtered if attack.severity == severity)
        return list(filtered)

    def category_counts(self) -> list[AttackCategoryCount]:
        counts = Counter(attack.category for attack in self._attacks)
        ordered_categories = sorted(AttackCategory, key=lambda category: category.value)
        return [
            AttackCategoryCount(category=category, count=counts.get(category, 0))
            for category in ordered_categories
        ]
