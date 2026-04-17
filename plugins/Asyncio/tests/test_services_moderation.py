import unittest

from ..services.moderation import check_moderation_flag


class ServicesModerationTestCase(unittest.IsolatedAsyncioTestCase):
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
