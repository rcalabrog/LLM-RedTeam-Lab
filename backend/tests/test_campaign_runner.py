import asyncio
import unittest

from app.attacks import AttackCategory, AttackLibrary, AttackSeverity
from app.core.config import Settings
from app.orchestration import CampaignRequestError, CampaignRunRequest, CampaignRunner, PipelineState
from app.targets.base import TargetApp
from app.targets.schemas import (
    TargetExecutionMetadata,
    TargetInvocationRequest,
    TargetInvocationResponse,
)


class FakeTarget(TargetApp):
    target_name = "fake_target"
    target_mode = "test"
    defense_mode = "none"
    description = "Fake target for runner unit tests."

    def __init__(self, *, default_model: str, fail_ids: set[str] | None = None) -> None:
        self._default_model = default_model
        self._fail_ids = fail_ids or set()

    async def invoke(self, request: TargetInvocationRequest) -> TargetInvocationResponse:
        attack_id = str(request.metadata.get("attack_id", ""))
        if attack_id in self._fail_ids:
            raise RuntimeError(f"Simulated target failure for {attack_id}")

        model = request.model_override or self._default_model
        return TargetInvocationResponse(
            target_name=self.target_name,
            target_mode=self.target_mode,
            defense_mode=self.defense_mode,
            model=model,
            response_text=f"handled:{attack_id}",
            warnings=["test_warning"] if "jb_" in attack_id else [],
            flags=["test_flag"] if "pi_" in attack_id else [],
            execution=TargetExecutionMetadata(
                final_prompt_summary="fake summary",
                llm_called=True,
                prompt_source="default_template",
                risk_level="low",
            ),
            metadata={"trace_id": f"trace-{attack_id}"},
        )


def build_test_settings() -> Settings:
    return Settings(
        DEFAULT_MAIN_MODEL="qwen3.5:9b",
        DEFAULT_TARGET="simple_vulnerable_chat",
        LLM_PROVIDER="ollama",
        OLLAMA_BASE_URL="http://localhost:11434",
        LLM_REQUEST_TIMEOUT_SECONDS=10,
    )


class TestCampaignRunner(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = build_test_settings()
        self.attack_library = AttackLibrary()

    def _build_runner(self, *, fail_ids: set[str] | None = None) -> CampaignRunner:
        def resolver(_target_name: str, settings: Settings) -> TargetApp:
            return FakeTarget(default_model=settings.default_main_model, fail_ids=fail_ids)

        return CampaignRunner(attack_library=self.attack_library, target_resolver=resolver)

    def test_select_all_attacks_in_canonical_order(self) -> None:
        runner = self._build_runner()
        attacks = runner.select_attacks(CampaignRunRequest(target_name="simple_vulnerable_chat"))
        ids = [attack.attack_id for attack in attacks]

        self.assertEqual(len(ids), 25)
        self.assertEqual(ids[0], "jb_001")
        self.assertEqual(ids[-1], "dl_005")

    def test_selection_combines_filters_with_intersection(self) -> None:
        runner = self._build_runner()
        attacks = runner.select_attacks(
            CampaignRunRequest(
                target_name="simple_vulnerable_chat",
                category=AttackCategory.policy_bypass,
                severity=AttackSeverity.high,
            )
        )

        self.assertEqual([attack.attack_id for attack in attacks], ["pb_002", "pb_004", "pb_005"])

    def test_selection_by_attack_ids_remains_deterministic(self) -> None:
        runner = self._build_runner()
        attacks = runner.select_attacks(
            CampaignRunRequest(
                target_name="simple_vulnerable_chat",
                attack_ids=["dl_004", "jb_003", "pi_002"],
            )
        )

        self.assertEqual([attack.attack_id for attack in attacks], ["jb_003", "pi_002", "dl_004"])

    def test_unknown_attack_id_raises_request_error(self) -> None:
        runner = self._build_runner()

        with self.assertRaises(CampaignRequestError):
            runner.select_attacks(
                CampaignRunRequest(
                    target_name="simple_vulnerable_chat",
                    attack_ids=["jb_001", "unknown_attack"],
                )
            )

    def test_partial_failure_continues_by_default(self) -> None:
        runner = self._build_runner(fail_ids={"pi_002"})
        request = CampaignRunRequest(
            campaign_name="partial-failure-test",
            target_name="simple_vulnerable_chat",
            attack_ids=["jb_001", "pi_002", "dl_001"],
            stop_on_error=False,
        )

        result = asyncio.run(runner.execute(request, self.settings))

        self.assertEqual(result.state, PipelineState.completed_with_errors)
        self.assertEqual(result.counts.selected_attacks, 3)
        self.assertEqual(result.counts.executed_attacks, 3)
        self.assertEqual(result.counts.failed_attacks, 1)
        self.assertEqual([item.attack_id for item in result.results], ["jb_001", "pi_002", "dl_001"])
        self.assertEqual(result.results[1].execution_status.value, "failed")
        self.assertEqual(result.results[1].attack_prompt_snapshot, self.attack_library.get_attack_by_id("pi_002").prompt)
        self.assertEqual(result.results[1].target_name_snapshot, "simple_vulnerable_chat")
        self.assertIsNone(result.results[1].execution_metadata.llm_called)

    def test_stop_on_error_halts_remaining_attacks(self) -> None:
        runner = self._build_runner(fail_ids={"pi_002"})
        request = CampaignRunRequest(
            campaign_name="stop-on-error-test",
            target_name="simple_vulnerable_chat",
            attack_ids=["jb_001", "pi_002", "dl_001"],
            stop_on_error=True,
        )

        result = asyncio.run(runner.execute(request, self.settings))

        self.assertEqual(result.state, PipelineState.completed_with_errors)
        self.assertEqual(result.counts.selected_attacks, 3)
        self.assertEqual(result.counts.executed_attacks, 2)
        self.assertEqual([item.attack_id for item in result.results], ["jb_001", "pi_002"])

    def test_campaign_result_contains_raw_fields_for_future_phases(self) -> None:
        runner = self._build_runner()
        request = CampaignRunRequest(
            campaign_name="shape-test",
            target_name="simple_vulnerable_chat",
            attack_ids=["jb_001"],
            model_override="llama3.1:8b",
            enabled_defenses=["context_sanitizer"],
            metadata={"suite": "smoke"},
        )

        result = asyncio.run(runner.execute(request, self.settings))
        attack_result = result.results[0]

        self.assertEqual(result.campaign_name, "shape-test")
        self.assertEqual(result.model_override, "llama3.1:8b")
        self.assertEqual(result.enabled_defenses, ["context_sanitizer"])
        self.assertEqual(attack_result.attack_id, "jb_001")
        self.assertEqual(attack_result.model, "llama3.1:8b")
        self.assertEqual(attack_result.target_name_snapshot, "fake_target")
        self.assertEqual(attack_result.defense_mode, "none")
        self.assertIsNotNone(attack_result.attack_prompt_snapshot)
        self.assertIsNotNone(attack_result.attack_description_snapshot)
        self.assertEqual(attack_result.execution_metadata.final_prompt_summary, "fake summary")
        self.assertEqual(attack_result.execution_metadata.risk_level, "low")
        self.assertEqual(attack_result.execution_metadata.target_mode, "test")
        self.assertEqual(attack_result.execution_metadata.raw_target_metadata["trace_id"], "trace-jb_001")
        self.assertIsNotNone(attack_result.started_at)
        self.assertIsNotNone(attack_result.completed_at)
        self.assertGreaterEqual(attack_result.completed_at, attack_result.started_at)


if __name__ == "__main__":
    unittest.main()
