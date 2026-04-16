# -*- coding: utf-8 -*-

import unittest

from ..core.chat import execute_chat_with_input_moderation


class _CooldownAllow:
    def __init__(self, events):
        self.events = events

    def should_wait_message(self, context_key, now, cooldown):
        _ = (context_key, now, cooldown)
        self.events.append("cooldown_check")
        return None

    def record(self, context_key, now):
        _ = (context_key, now)
        self.events.append("cooldown_record")


class _CooldownBlock:
    def should_wait_message(self, context_key, now, cooldown):
        _ = (context_key, now, cooldown)
        return "Please wait 1s before sending another request."

    def record(self, context_key, now):
        raise AssertionError("record should not be called when cooldown blocks")


class CoreChatTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_gate_order_and_success_path(self):
        events = []

        def fake_count_tokens(text):
            _ = text
            events.append("count_tokens")
            return 2

        async def fake_check_moderation(text):
            _ = text
            events.append("moderation")
            return False

        async def fake_chat_with_model(user_request, context_key, config):
            _ = (user_request, context_key, config)
            events.append("chat")
            return "ok"

        response = await execute_chat_with_input_moderation(
            "hello there",
            context_key="#chan:alice",
            config={"cooldown": 5, "max_tokens": 10},
            cooldown_manager=_CooldownAllow(events),
            check_moderation_flag_fn=fake_check_moderation,
            chat_with_model_fn=fake_chat_with_model,
            count_tokens_fn=fake_count_tokens,
            now_fn=lambda: 100.0,
        )

        self.assertEqual(response, "ok")
        self.assertEqual(
            events,
            ["cooldown_check", "cooldown_record", "count_tokens", "moderation", "chat"],
        )

    async def test_cooldown_blocks_early(self):
        response = await execute_chat_with_input_moderation(
            "hello",
            context_key="#chan:alice",
            config={"cooldown": 5, "max_tokens": 10},
            cooldown_manager=_CooldownBlock(),
            now_fn=lambda: 100.0,
        )
        self.assertIn("Please wait", response)

    async def test_token_limit_blocks_before_moderation(self):
        events = []

        async def fake_check_moderation(_text):
            events.append("moderation")
            return False

        async def fake_chat_with_model(_a, _b, _c):
            events.append("chat")
            return "ok"

        response = await execute_chat_with_input_moderation(
            "too many tokens",
            context_key="#chan:alice",
            config={"cooldown": 5, "max_tokens": 1},
            cooldown_manager=_CooldownAllow(events),
            check_moderation_flag_fn=fake_check_moderation,
            chat_with_model_fn=fake_chat_with_model,
            count_tokens_fn=lambda _text: 2,
            now_fn=lambda: 100.0,
        )

        self.assertIn("exceeds the max token limit", response)
        self.assertEqual(events, ["cooldown_check", "cooldown_record"])

    async def test_moderation_blocks_before_chat(self):
        events = []

        async def fake_check_moderation(_text):
            events.append("moderation")
            return True

        async def fake_chat_with_model(_a, _b, _c):
            events.append("chat")
            return "ok"

        response = await execute_chat_with_input_moderation(
            "hello",
            context_key="#chan:alice",
            config={"cooldown": 5, "max_tokens": 10},
            cooldown_manager=_CooldownAllow(events),
            check_moderation_flag_fn=fake_check_moderation,
            chat_with_model_fn=fake_chat_with_model,
            count_tokens_fn=lambda _text: 2,
            now_fn=lambda: 100.0,
        )

        self.assertIn("flagged as inappropriate", response)
        self.assertEqual(events, ["cooldown_check", "cooldown_record", "moderation"])
