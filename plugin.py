###
# Copyright (c) 2026, Barry Suridge
# All rights reserved.
#
#
###

from collections import deque
from pathlib import Path
from typing import List

from supybot import callbacks
from supybot import ircmsgs
from supybot.commands import *
from supybot.i18n import PluginInternationalization

_ = PluginInternationalization("MessagesLog")


class MessagesLog(callbacks.Plugin):
    """Access Limnoria's messages.log"""

    threaded = True

    def _log_path(self) -> Path:
        return Path(str(self.registryValue("logFilePath"))).expanduser()

    @staticmethod
    def _read_last_lines(path: Path, line_count: int) -> List[str]:
        if line_count <= 0:
            return []
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return [line.rstrip("\r\n") for line in deque(handle, maxlen=line_count)]

    def tail(self, irc, msg, args, line_count):
        """[<line count>]

        Reads lines from the end of messages.log. If <line count> is not
        provided, uses the configured default.
        """
        self._tail_impl(irc, msg, line_count=line_count)

    def _tail_impl(self, irc, msg, line_count=None):
        requested_line_count = (
            int(line_count)
            if line_count is not None
            else int(self.registryValue("lineCount"))
        )
        max_line_count = int(self.registryValue("maxLineCount"))
        line_count = min(requested_line_count, max_line_count)
        log_path = self._log_path()

        try:
            lines = self._read_last_lines(log_path, line_count)
        except FileNotFoundError:
            irc.error(_("Log file not found: %s") % log_path)
            return
        except OSError as error:
            irc.error(_("Unable to read log file: %s") % error)
            return

        if not lines:
            irc.reply(_("Log file is empty."))
            return

        for line in lines:
            irc.sendMsg(ircmsgs.notice(msg.nick, line))
        irc.reply(_("Sent %s log lines by notice.") % len(lines))

    tail = wrap(tail, [("checkCapability", "admin"), optional("positiveInt")])


Class = MessagesLog


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
