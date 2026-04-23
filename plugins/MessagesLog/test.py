###
# Copyright (c) 2026, Barry Suridge
# All rights reserved.
#
#
###

import tempfile
from pathlib import Path
import unittest
from unittest import mock

from supybot.test import *

try:
    from . import plugin
except ImportError:  # pragma: no cover - allows direct unittest execution.
    import plugin


class MessagesLogTestCase(PluginTestCase):
    plugins = ("MessagesLog",)


class TestMessagesLogInternal(unittest.TestCase):
    def test_read_last_lines_returns_only_tail(self):
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as handle:
            handle.write("line1\nline2\nline3\nline4\n")
            log_path = Path(handle.name)
        self.addCleanup(log_path.unlink)

        lines = plugin.MessagesLog._read_last_lines(log_path, 2)

        self.assertEqual(lines, ["line3", "line4"])

    def test_tail_uses_configured_line_count_and_replies(self):
        messages_log = plugin.MessagesLog.__new__(plugin.MessagesLog)
        messages_log.registryValue = mock.Mock(
            side_effect=lambda key: {
                "lineCount": 20,
                "maxLineCount": 100,
            }[key]
        )
        messages_log._log_path = mock.Mock(return_value=Path("/tmp/messages.log"))
        messages_log._read_last_lines = mock.Mock(return_value=["entry1", "entry2"])
        irc = mock.Mock()

        messages_log._tail_impl(irc)

        messages_log._read_last_lines.assert_called_once_with(
            Path("/tmp/messages.log"), 20
        )
        irc.replies.assert_called_once_with(
            ["entry1", "entry2"], prefixNick=False, oneToOne=False
        )

    def test_tail_reports_missing_file(self):
        messages_log = plugin.MessagesLog.__new__(plugin.MessagesLog)
        messages_log.registryValue = mock.Mock(
            side_effect=lambda key: {
                "lineCount": 20,
                "maxLineCount": 100,
            }[key]
        )
        messages_log._log_path = mock.Mock(return_value=Path("/tmp/messages.log"))
        messages_log._read_last_lines = mock.Mock(side_effect=FileNotFoundError)
        irc = mock.Mock()

        messages_log._tail_impl(irc)

        irc.error.assert_called_once()
        irc.replies.assert_not_called()

    def test_tail_uses_argument_override_when_provided(self):
        messages_log = plugin.MessagesLog.__new__(plugin.MessagesLog)
        messages_log.registryValue = mock.Mock(
            side_effect=lambda key: {
                "lineCount": 20,
                "maxLineCount": 100,
            }[key]
        )
        messages_log._log_path = mock.Mock(return_value=Path("/tmp/messages.log"))
        messages_log._read_last_lines = mock.Mock(return_value=["entry1"])
        irc = mock.Mock()

        messages_log._tail_impl(irc, line_count=7)

        messages_log._read_last_lines.assert_called_once_with(
            Path("/tmp/messages.log"), 7
        )
        irc.replies.assert_called_once_with(
            ["entry1"], prefixNick=False, oneToOne=False
        )

    def test_tail_caps_argument_to_max_line_count(self):
        messages_log = plugin.MessagesLog.__new__(plugin.MessagesLog)
        messages_log.registryValue = mock.Mock(
            side_effect=lambda key: {
                "lineCount": 20,
                "maxLineCount": 10,
            }[key]
        )
        messages_log._log_path = mock.Mock(return_value=Path("/tmp/messages.log"))
        messages_log._read_last_lines = mock.Mock(return_value=["entry1"])
        irc = mock.Mock()

        messages_log._tail_impl(irc, line_count=50)

        messages_log._read_last_lines.assert_called_once_with(
            Path("/tmp/messages.log"), 10
        )


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
