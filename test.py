###
# Copyright (c) 2020 - 2026, Barry Suridge
# All rights reserved.
#
#
###

import subprocess  # nosec B404
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from supybot.test import ChannelPluginTestCase as SupybotChannelPluginTestCase

from . import plugin

SupybotChannelPluginTestCase.__test__ = False


class MyPingTestCase(SupybotChannelPluginTestCase):
    __test__ = False

    plugins = ("MyPing",)
    config = {"supybot.plugins.myping.enable": True}

    @staticmethod
    def _successful_ping_output():
        return (
            "PING google.com (142.250.66.14): 56 data bytes\n"
            "64 bytes from 142.250.66.14: icmp_seq=0 ttl=57 time=23.4 ms\n"
            "\n"
            "--- google.com ping statistics ---\n"
            "1 packets transmitted, 1 received, 0% packet loss, time 0ms\n"
            "round-trip min/avg/max = 23.400/23.400/23.400 ms"
        )

    @patch("MyPing.plugin.subprocess.check_output")
    def testPingReachable(self, mock_check_output):
        mock_check_output.return_value = self._successful_ping_output()
        self.assertRegexp("myping ping google.com", "is Reachable")

    @patch("MyPing.plugin.subprocess.check_output")
    def testPingNotReachable(self, mock_check_output):
        mock_check_output.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["ping", "google.com"]
        )
        self.assertRegexp("myping ping google.com", "Not Reachable")

    @patch("MyPing.plugin.subprocess.check_output")
    def testPingTimeout(self, mock_check_output):
        mock_check_output.side_effect = subprocess.TimeoutExpired(
            cmd=["ping", "google.com"], timeout=3.0
        )
        self.assertRegexp("myping ping google.com", "Not Reachable")


class MyPingSecurityTestCase(unittest.TestCase):
    def test_rejects_option_like_target(self):
        is_valid, _, error = plugin._valid_ping_target("-c")

        self.assertFalse(is_valid)
        self.assertIn("must not start", error)

    def test_rejects_control_characters(self):
        is_valid, _, error = plugin._valid_ping_target("example.com\x02")

        self.assertFalse(is_valid)
        self.assertIn("invalid characters", error)

    def test_rejects_oversized_target(self):
        is_valid, _, error = plugin._valid_ping_target("a" * 254)

        self.assertFalse(is_valid)
        self.assertIn("too long", error)

    def test_elapsed_loss_handles_unexpected_output(self):
        self.assertIn(
            "unavailable",
            plugin._elapsed_loss("unexpected ping output"),
        )

    def test_reply_text_is_capped(self):
        result = plugin._limit_text("A" * 500)

        self.assertEqual(len(result), plugin.MAX_REPLY_LENGTH)
        self.assertTrue(result.endswith("..."))

    def test_cooldown_is_per_user_and_prunes_expired_entries(self):
        resolver = plugin.MyPing.__new__(plugin.MyPing)
        resolver._cooldowns = {("net", "#test", "old!user@example"): 1.0}
        resolver._cooldown_lock = threading.Lock()
        resolver.registryValue = lambda name, channel: 5

        irc = SimpleNamespace(network="net")
        msg = SimpleNamespace(prefix="new!user@example")

        with patch("time.monotonic", return_value=10.0):
            self.assertEqual(
                resolver._cooldown_remaining(irc, msg, "#test"), 0
            )

        self.assertNotIn(
            ("net", "#test", "old!user@example"), resolver._cooldowns
        )


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
