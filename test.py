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

from supybot import ircmsgs
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
        msg = mock.Mock(nick="Barry")

        messages_log._tail_impl(irc, msg)

        messages_log._read_last_lines.assert_called_once_with(
            Path("/tmp/messages.log"), 20
        )
        self.assertEqual(
            irc.sendMsg.call_args_list,
            [
                mock.call(ircmsgs.notice("Barry", "entry1")),
                mock.call(ircmsgs.notice("Barry", "entry2")),
            ],
        )
        irc.reply.assert_called_once_with("Sent 2 log lines by notice.")

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
        msg = mock.Mock(nick="Barry")

        messages_log._tail_impl(irc, msg)

        irc.error.assert_called_once()
        irc.sendMsg.assert_not_called()

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
        msg = mock.Mock(nick="Barry")

        messages_log._tail_impl(irc, msg, line_count=7)

        messages_log._read_last_lines.assert_called_once_with(
            Path("/tmp/messages.log"), 7
        )
        irc.sendMsg.assert_called_once_with(ircmsgs.notice("Barry", "entry1"))
        irc.reply.assert_called_once_with("Sent 1 log lines by notice.")

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
        msg = mock.Mock(nick="Barry")

        messages_log._tail_impl(irc, msg, line_count=50)

        messages_log._read_last_lines.assert_called_once_with(
            Path("/tmp/messages.log"), 10
        )


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
