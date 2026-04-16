# -*- coding: utf-8 -*-

from types import SimpleNamespace
import unittest

from ..state.memory import (
    USER_HISTORIES,
    clear_context_history,
    clear_history,
    get_user_history,
    make_context_key,
    trim_history,
)


class StateMemoryTestCase(unittest.TestCase):
    def setUp(self):
        clear_history()

    def tearDown(self):
        clear_history()

    def test_make_context_key(self):
        msg = SimpleNamespace(nick="alice", channel="#test")
        self.assertEqual(make_context_key(msg), "#test:alice")

        pm_msg = SimpleNamespace(nick="alice")
        self.assertEqual(make_context_key(pm_msg), "PM:alice")

    def test_get_user_history_initializes_and_updates_system_prompt(self):
        history = get_user_history("ctx", "prompt-a")
        self.assertEqual(history, [{"role": "system", "content": "prompt-a"}])

        history = get_user_history("ctx", "prompt-b")
        self.assertEqual(history[0]["content"], "prompt-b")

    def test_trim_history_keeps_system_plus_last_ten(self):
        history = get_user_history("ctx", "prompt")
        for i in range(15):
            history.append({"role": "user", "content": str(i)})

        trimmed = trim_history("ctx", max_messages=12)
        self.assertEqual(len(trimmed), 11)
        self.assertEqual(trimmed[0]["role"], "system")
        self.assertEqual(trimmed[-1]["content"], "14")

    def test_clear_context_history(self):
        get_user_history("ctx", "prompt")
        self.assertIn("ctx", USER_HISTORIES)
        clear_context_history("ctx")
        self.assertNotIn("ctx", USER_HISTORIES)
