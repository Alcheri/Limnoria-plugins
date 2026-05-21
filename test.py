###
# Copyright (c) 2026, Barry Suridge
# All rights reserved.
###

import unittest
import threading
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from supybot.test import PluginTestCase as SupybotPluginTestCase

SupybotPluginTestCase.__test__ = False


class WorldTimeTestCase(SupybotPluginTestCase):
    __test__ = False
    plugins = ("WorldTime",)


class WorldTimeSmokeTestCase(unittest.TestCase):
    def setUp(self):
        try:
            from . import plugin
        except ImportError:
            import plugin

        self.plugin_module = plugin

    def _plugin(self):
        resolver = self.plugin_module.WorldTime.__new__(
            self.plugin_module.WorldTime
        )
        resolver.db = {}
        resolver._cooldowns = {}
        resolver._cooldown_lock = threading.Lock()
        resolver.registryValue = MagicMock(
            side_effect=lambda name, channel=None: {
                "cooldownSeconds": 5,
                "maxResponseBytes": 262144,
            }.get(name, 0)
        )
        return resolver

    def test_plugin_module_exports_class(self):
        self.assertTrue(hasattr(self.plugin_module, "Class"))

    def test_validate_location_rejects_oversized_value(self):
        resolver = self._plugin()

        is_valid, _, error = resolver._validate_location("a" * 121)

        self.assertFalse(is_valid)
        self.assertIn("too long", error)

    def test_clean_text_preserves_irc_formatting(self):
        resolver = self._plugin()

        result = resolver._clean_text("\x02Sydney\x02\x00")

        self.assertIn("\x02", result)
        self.assertNotIn("\x00", result)

    def test_cooldown_is_per_user_and_channel(self):
        resolver = self._plugin()
        irc = SimpleNamespace(network="testnet")
        msg = SimpleNamespace(args=["#test"], prefix="user!ident@example")

        with patch("time.monotonic", return_value=100.0):
            self.assertEqual(resolver._cooldown_remaining(irc, msg), 0)
        with patch("time.monotonic", return_value=101.0):
            self.assertEqual(resolver._cooldown_remaining(irc, msg), 4)

    def test_set_rejects_oversized_location(self):
        resolver = self._plugin()

        is_valid, error = resolver._store_location(
            "nick!ident@example", "a" * 121
        )

        self.assertFalse(is_valid)
        self.assertIn("too long", error)
        self.assertEqual(resolver.db, {})


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
