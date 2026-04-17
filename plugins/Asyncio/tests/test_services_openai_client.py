import unittest
from unittest import mock

from ..services.openai_client import create_chat_completion_with_fallback
from ..state.runtime import OpenAIRuntimeState


class _FakeCompletions:
    def __init__(self, behaviors):
        self.behaviors = list(behaviors)
        self.calls = []

    def create(self, model, **kwargs):
        self.calls.append((model, kwargs))
        behavior = self.behaviors.pop(0)
        if isinstance(behavior, Exception):
            raise behavior
        return behavior


class _FakeClient:
    def __init__(self, completions):
        self.chat = type("Chat", (), {"completions": completions})


class ServicesOpenAIClientTestCase(unittest.TestCase):
    def test_fallback_uses_next_model_when_deprecated(self):
        completions = _FakeCompletions(
            [
                Exception("model is deprecated and no longer available"),
                "ok-response",
            ]
        )
        client = _FakeClient(completions)
        state = OpenAIRuntimeState()

        with mock.patch.dict(
            "os.environ",
            {"OPENAI_CHAT_MODELS": "gpt-4o-mini,gpt-4.1-mini"},
            clear=False,
        ):
            response = create_chat_completion_with_fallback(
                client,
                state,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=10,
                temperature=0.1,
                top_p=0.9,
            )

        self.assertEqual(response, "ok-response")
        self.assertEqual(
            [call[0] for call in completions.calls], ["gpt-4o-mini", "gpt-4.1-mini"]
        )
        self.assertEqual(state.active_chat_model, "gpt-4.1-mini")

    def test_non_model_error_is_raised(self):
        completions = _FakeCompletions([Exception("connection reset")])
        client = _FakeClient(completions)
        state = OpenAIRuntimeState()

        with self.assertRaises(Exception):
            create_chat_completion_with_fallback(
                client,
                state,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=10,
                temperature=0.1,
                top_p=0.9,
            )
