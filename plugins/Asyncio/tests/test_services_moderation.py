import unittest
from types import SimpleNamespace
from unittest import mock

from ..services import moderation
from ..services.moderation import ModerationResult, check_moderation_flag


class ServicesModerationTestCase(unittest.IsolatedAsyncioTestCase):
    def test_moderation_response_retains_only_flag_categories(self):
        response = SimpleNamespace(
            _request_id="req_moderation_123",
            results=[
                SimpleNamespace(
                    flagged=True,
                    categories=SimpleNamespace(
                        model_dump=lambda: {
                            "sexual": True,
                            "self-harm": False,
                            "violence": True,
                        }
                    ),
                )
            ],
        )

        result = moderation._get_moderation_result(response)

        self.assertEqual(
            result,
            ModerationResult(
                flagged=True,
                categories=("sexual", "violence"),
                request_id="req_moderation_123",
            ),
        )

    async def test_short_or_command_input_bypasses_moderation(self):
        called = {"count": 0}

        async def fake_to_thread(func, text):
            _ = (func, text)
            called["count"] += 1
            return False

        flagged = await check_moderation_flag(
            "!cmd",
            to_thread_fn=fake_to_thread,
        )
        self.assertFalse(flagged)
        self.assertEqual(called["count"], 0)

    async def test_rate_limit_retries_then_succeeds(self):
        attempts = {"count": 0}
        sleeps = []

        async def fake_to_thread(func, text):
            _ = (func, text)
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise Exception("429 Too Many Requests")
            return True

        async def fake_sleep(duration):
            sleeps.append(duration)

        flagged = await check_moderation_flag(
            "this should be moderated",
            to_thread_fn=fake_to_thread,
            sleep_fn=fake_sleep,
            random_uniform_fn=lambda _a, _b: 0.0,
        )

        self.assertTrue(flagged)
        self.assertEqual(attempts["count"], 3)
        self.assertEqual(sleeps, [1.0, 2.0])

    async def test_flagged_result_logs_categories_without_message_text(self):
        async def fake_to_thread(_func, _text):
            return ModerationResult(
                flagged=True,
                categories=("sexual", "violence"),
                request_id="req_moderation_123",
            )

        with mock.patch.object(moderation.log, "warning") as warning:
            flagged = await check_moderation_flag(
                "sensitive user message",
                context_key="#channel:alice",
                to_thread_fn=fake_to_thread,
            )

        self.assertTrue(flagged)
        warning.assert_called_once_with(
            "[Asyncio] Moderation blocked request for #channel:alice: "
            "categories=sexual, violence, request_id=req_moderation_123"
        )
