import unittest

from pydantic import ValidationError

from app.targets.schemas import TargetExecutionMetadata, TargetInvocationRequest, TargetInvocationResponse


class TestTargetSchemas(unittest.TestCase):
    def test_request_defaults_are_applied(self) -> None:
        request = TargetInvocationRequest(user_input="hello")

        self.assertEqual(request.user_input, "hello")
        self.assertIsNone(request.system_prompt_override)
        self.assertIsNone(request.model_override)
        self.assertEqual(request.tags, [])
        self.assertEqual(request.metadata, {})

    def test_request_rejects_empty_user_input(self) -> None:
        with self.assertRaises(ValidationError):
            TargetInvocationRequest(user_input="")

    def test_response_schema_shape(self) -> None:
        response = TargetInvocationResponse(
            target_name="simple_vulnerable_chat",
            target_mode="vulnerable",
            defense_mode="none",
            model="qwen3.5:9b",
            response_text="hello",
            execution=TargetExecutionMetadata(
                final_prompt_summary="summary",
                llm_called=True,
                prompt_source="default_template",
            ),
        )

        self.assertEqual(response.target_name, "simple_vulnerable_chat")
        self.assertEqual(response.warnings, [])
        self.assertEqual(response.flags, [])


if __name__ == "__main__":
    unittest.main()
