import unittest

from app.attacks import AttackCategory, AttackLibrary, AttackSeverity


class TestAttackLibrary(unittest.TestCase):
    def setUp(self) -> None:
        self.library = AttackLibrary()

    def test_summary_has_all_mvp_categories_with_counts(self) -> None:
        summary = self.library.summarize_categories()
        category_counts = {item.category: item.count for item in summary}

        self.assertEqual(len(category_counts), 5)
        self.assertEqual(sum(category_counts.values()), 25)
        self.assertEqual(category_counts[AttackCategory.jailbreak_basic], 5)
        self.assertEqual(category_counts[AttackCategory.prompt_injection_direct], 5)
        self.assertEqual(category_counts[AttackCategory.system_prompt_extraction], 5)
        self.assertEqual(category_counts[AttackCategory.policy_bypass], 5)
        self.assertEqual(category_counts[AttackCategory.data_leakage_simulation], 5)

    def test_filtering_by_category(self) -> None:
        attacks = self.library.get_attacks_by_category(AttackCategory.prompt_injection_direct)
        self.assertTrue(attacks)
        self.assertTrue(all(attack.category == AttackCategory.prompt_injection_direct for attack in attacks))

    def test_filtering_by_severity(self) -> None:
        attacks = self.library.query_attacks(severity=AttackSeverity.high)
        self.assertTrue(attacks)
        self.assertTrue(all(attack.severity == AttackSeverity.high for attack in attacks))

    def test_lookup_by_attack_id(self) -> None:
        attack = self.library.get_attack_by_id("spe_003")
        self.assertIsNotNone(attack)
        assert attack is not None
        self.assertEqual(attack.attack_id, "spe_003")
        self.assertEqual(attack.category, AttackCategory.system_prompt_extraction)

    def test_get_attacks_by_ids_returns_existing_only(self) -> None:
        attacks = self.library.get_attacks_by_ids(["jb_001", "missing_id", "dl_002"])
        ids = [attack.attack_id for attack in attacks]
        self.assertEqual(ids, ["jb_001", "dl_002"])


if __name__ == "__main__":
    unittest.main()
