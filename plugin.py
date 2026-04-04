# -*- coding: utf-8 -*-
###
# Copyright (c) 2016 - 2026, Barry Suridge
# All rights reserved.
#

import random
from pathlib import Path

import supybot.ircutils as utils
import supybot.callbacks as callbacks


class OnJoin(callbacks.Plugin):
    """Send a notice to all users entering a channel."""

    public = False

    def doJoin(self, irc, msg):
        """Send a random notice to a user
        when they enter the channel."""

        channel = msg.args[0]
        if not self.registryValue("enable", channel):
            return
        if utils.strEqual(irc.nick, msg.nick):
            return

        selected_line = self._read_random_quote()
        if selected_line is None:
            return

        irc.reply(
            self._teal(selected_line.strip()),
            notice=True,
            private=True,
            to=msg.nick,
        )

    def _read_random_quote(self):
        """Return one random line from quotes.txt, or None on read error."""

        quotes_path = Path(__file__).with_name("quotes.txt")
        line_num = 0
        selected_line = ""
        try:
            with quotes_path.open(encoding="utf-8") as quote_file:
                for line in quote_file:
                    line_num += 1
                    if random.uniform(0, line_num) < 1:
                        selected_line = line
        except OSError as err:
            self.log.warning("OnJoin: failed to read %s: %s", quotes_path, err)
            return None
        return selected_line

    def _teal(self, string):
        """Return a teal coloured string."""
        return utils.bold(utils.mircColor(string, "teal"))


Class = OnJoin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
