import unittest
from unittest import mock

from ..services.openai_client import (
    _chat_model_candidates,
    _prepare_chat_completion_kwargs,
    create_chat_completion_with_fallback,
)
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
    def test_default_models_use_current_fallbacks(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertEqual(
                _chat_model_candidates(),
                [
                    "gpt-5.6-luna",
                    "gpt-5.6-terra",
                    "gpt-5.6-sol",
                    "gpt-5.5",
                ],
            )

    def test_gpt5_kwargs_use_completion_token_limit(self):
        request_kwargs = _prepare_chat_completion_kwargs(
            "gpt-5.5",
            {
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 10,
                "temperature": 0.1,
                "top_p": 0.9,
            },
        )

        self.assertEqual(request_kwargs["max_completion_tokens"], 10)
        self.assertNotIn("max_tokens", request_kwargs)
        self.assertNotIn("temperature", request_kwargs)
        self.assertNotIn("top_p", request_kwargs)

    def test_non_gpt5_kwargs_keep_legacy_parameters(self):
        request_kwargs = _prepare_chat_completion_kwargs(
            "custom-chat-model",
            {
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 10,
                "temperature": 0.1,
                "top_p": 0.9,
            },
        )

        self.assertEqual(request_kwargs["max_tokens"], 10)
        self.assertEqual(request_kwargs["temperature"], 0.1)
        self.assertEqual(request_kwargs["top_p"], 0.9)

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
            {"OPENAI_CHAT_MODELS": "gpt-5.5,gpt-5.4-mini"},
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
            [call[0] for call in completions.calls],
            ["gpt-5.5", "gpt-5.4-mini"],
        )
        self.assertEqual(
            completions.calls[1][1]["max_completion_tokens"],
            10,
        )
        self.assertNotIn("max_tokens", completions.calls[1][1])
        self.assertEqual(state.active_chat_model, "gpt-5.4-mini")

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
