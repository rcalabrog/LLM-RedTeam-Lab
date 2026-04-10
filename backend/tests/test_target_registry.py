import unittest

from app.core.config import Settings
from app.targets.base import TargetNotFoundError
from app.targets.guarded_chat_target import GuardedChatTarget
from app.targets.registry import get_default_target, get_target, list_available_targets
from app.targets.simple_chat_target import SimpleVulnerableChatTarget


class TestTargetRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = Settings(
            DEFAULT_TARGET="simple_vulnerable_chat",
            DEFAULT_MAIN_MODEL="qwen3.5:9b",
            LLM_PROVIDER="ollama",
            OLLAMA_BASE_URL="http://localhost:11434",
            LLM_REQUEST_TIMEOUT_SECONDS=10,
        )

    def test_lists_expected_targets(self) -> None:
        targets = list_available_targets()
        names = [target.name for target in targets]

        self.assertIn("simple_vulnerable_chat", names)
        self.assertIn("guarded_chat", names)

    def test_get_target_returns_vulnerable_target(self) -> None:
        target = get_target("simple_vulnerable_chat", self.settings)
        self.assertIsInstance(target, SimpleVulnerableChatTarget)

    def test_get_target_returns_guarded_target(self) -> None:
        target = get_target("guarded_chat", self.settings)
        self.assertIsInstance(target, GuardedChatTarget)

    def test_get_default_target_uses_settings(self) -> None:
        target = get_default_target(self.settings)
        self.assertIsInstance(target, SimpleVulnerableChatTarget)

    def test_get_target_raises_for_unknown_name(self) -> None:
        with self.assertRaises(TargetNotFoundError):
            get_target("does-not-exist", self.settings)


if __name__ == "__main__":
    unittest.main()
