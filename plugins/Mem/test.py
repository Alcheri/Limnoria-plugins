###
# Copyright (c) 2026, Barry Suridge
# All rights reserved.
#
#
###

from types import SimpleNamespace
import unittest
from unittest import mock

import supybot.test as supybot_test

from . import plugin

supybot_test.PluginTestCase.__test__ = False


class MemTestCase(supybot_test.PluginTestCase):
    __test__ = False
    plugins = ("Mem",)

    def test_mem_usage(self):
        self.assertNotError("mem usage")

    def test_mem_top(self):
        self.assertNotError("mem top")

    def test_mem_stats(self):
        self.assertNotError("mem stats")

    def test_mem_unknown_subcommand(self):
        self.assertResponse(
            "mem unknown",
            "Unknown subcommand. Use: usage, top, stats.",
        )


class MemInternalTestCase(unittest.TestCase):
    def test_has_admin_capability_delegates_to_limnoria(self):
        msg = SimpleNamespace(prefix="nick!user@example")

        with mock.patch.object(
            plugin.ircdb, "checkCapability", return_value=True
        ) as check:
            self.assertTrue(plugin._has_admin_capability(msg))

        check.assert_called_once_with("nick!user@example", "admin")

    def test_mem_top_requires_admin_capability(self):
        mem_plugin = plugin.Mem.__new__(plugin.Mem)
        mem_plugin.log = mock.Mock()
        irc = mock.Mock()
        msg = SimpleNamespace(prefix="nick!user@example")

        with (
            mock.patch.object(
                plugin.ircdb, "checkCapability", return_value=False
            ),
            mock.patch.object(mem_plugin, "_top") as top,
        ):
            plugin.Mem.mem(mem_plugin, irc, msg, ["top"])

        top.assert_not_called()
        irc.error.assert_called_once_with(
            "The mem top subcommand requires admin capability.",
            prefixNick=False,
        )

    def test_mem_top_runs_for_admins(self):
        mem_plugin = plugin.Mem.__new__(plugin.Mem)
        mem_plugin.log = mock.Mock()
        irc = mock.Mock()
        msg = SimpleNamespace(prefix="nick!user@example")

        with (
            mock.patch.object(
                plugin.ircdb, "checkCapability", return_value=True
            ),
            mock.patch.object(mem_plugin, "_top") as top,
        ):
            plugin.Mem.mem(mem_plugin, irc, msg, ["top"])

        top.assert_called_once_with(irc, 5)

    def test_mem_usage_remains_public(self):
        mem_plugin = plugin.Mem.__new__(plugin.Mem)
        mem_plugin.log = mock.Mock()
        irc = mock.Mock()
        msg = SimpleNamespace(prefix="nick!user@example")

        with mock.patch.object(mem_plugin, "_usage") as usage:
            plugin.Mem.mem(mem_plugin, irc, msg, ["usage"])

        usage.assert_called_once_with(irc)

    def test_tracemalloc_already_tracing(self):
        with (
            mock.patch.object(
                plugin.callbacks.Plugin, "__init__", return_value=None
            ),
            mock.patch.object(
                plugin.tracemalloc, "is_tracing", return_value=True
            ),
            mock.patch.object(plugin.tracemalloc, "start") as mock_start,
        ):
            plugin.Mem(mock.sentinel.irc)
            mock_start.assert_not_called()

    def test_tracemalloc_not_tracing(self):
        with (
            mock.patch.object(
                plugin.callbacks.Plugin, "__init__", return_value=None
            ),
            mock.patch.object(
                plugin.tracemalloc, "is_tracing", return_value=False
            ),
            mock.patch.object(plugin.tracemalloc, "start") as mock_start,
        ):
            plugin.Mem(mock.sentinel.irc)
            mock_start.assert_called_once_with()

    def test_stats_handles_missing_optional_fields(self):
        mock_irc = mock.Mock()
        memory_info = SimpleNamespace(
            rss=10 * 1024 * 1024,
            vms=20 * 1024 * 1024,
        )
        mock_process = mock.Mock()
        mock_process.memory_info.return_value = memory_info

        with mock.patch.object(
            plugin.psutil, "Process", return_value=mock_process
        ):
            mem_plugin = plugin.Mem.__new__(plugin.Mem)
            mem_plugin._stats(mock_irc)

        mock_irc.reply.assert_called_once_with(
            "RSS: 10 MB; VMS: 20 MB; Shared: 0 MB; Data: 0 MB"
        )

    def test_top_handles_empty_snapshot(self):
        mock_irc = mock.Mock()
        mock_snapshot = mock.Mock()
        mock_snapshot.statistics.return_value = []

        with mock.patch.object(
            plugin.tracemalloc, "take_snapshot", return_value=mock_snapshot
        ):
            mem_plugin = plugin.Mem.__new__(plugin.Mem)
            mem_plugin._top(mock_irc, 5)

        mock_irc.reply.assert_called_once_with(
            "No allocation statistics available yet."
        )


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
