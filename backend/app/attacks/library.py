from .catalog import AttackCatalog
from .schemas import AttackCategory, AttackCategoryCount, AttackDefinition, AttackSeverity


class AttackLibrary:
    """Service interface used by routes and future orchestration code."""

    def __init__(self, catalog: AttackCatalog | None = None) -> None:
        self._catalog = catalog or AttackCatalog()

    def get_all_attacks(self) -> list[AttackDefinition]:
        return self._catalog.all()

    def get_attacks_by_category(self, category: AttackCategory) -> list[AttackDefinition]:
        return self._catalog.filter(category=category)

    def get_attacks_by_ids(self, attack_ids: list[str]) -> list[AttackDefinition]:
        results: list[AttackDefinition] = []
        for attack_id in attack_ids:
            attack = self._catalog.get(attack_id)
            if attack is not None:
                results.append(attack)
        return results

    def get_attack_by_id(self, attack_id: str) -> AttackDefinition | None:
        return self._catalog.get(attack_id)

    def query_attacks(
        self,
        *,
        category: AttackCategory | None = None,
        severity: AttackSeverity | None = None,
    ) -> list[AttackDefinition]:
        return self._catalog.filter(category=category, severity=severity)

    def summarize_categories(self) -> list[AttackCategoryCount]:
        return self._catalog.category_counts()
