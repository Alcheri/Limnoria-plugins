###
# Copyright (c) 2016 - 2026, Barry Suridge
# All rights reserved.
#

import random
from pathlib import Path

import supybot.ircutils as utils
import supybot.callbacks as callbacks
from supybot.commands import optional, wrap

DEFAULT_RECENT_QUOTES = 5


class OnJoin(callbacks.Plugin):
    """Send a notice to all users entering a channel."""

    public = False

    def _quotes_path(self):
        return Path(__file__).with_name("quotes.txt")

    def _normalise_quote(self, text):
        quote = " ".join(text.splitlines()).strip()
        return quote or None

    def _load_quotes(self):
        quotes_path = self._quotes_path()
        try:
            with quotes_path.open(encoding="utf-8") as quote_file:
                return [line.rstrip("\n") for line in quote_file if line.strip()]
        except OSError as err:
            self.log.warning("OnJoin: failed to read %s: %s", quotes_path, err)
            return None

    def _write_quotes(self, quotes):
        quotes_path = self._quotes_path()
        try:
            with quotes_path.open("w", encoding="utf-8") as quote_file:
                for quote in quotes:
                    quote_file.write(f"{quote}\n")
        except OSError as err:
            self.log.warning("OnJoin: failed to write %s: %s", quotes_path, err)
            return False
        return True

    def _append_quote(self, text):
        quote = self._normalise_quote(text)
        if quote is None:
            return None

        quotes = self._load_quotes()
        if quotes is None:
            return False

        quotes.append(quote)
        max_quotes = self.registryValue("maxQuotes")
        if len(quotes) > max_quotes:
            quotes = quotes[-max_quotes:]

        if not self._write_quotes(quotes):
            return False
        return quote

    def _recent_quotes(self, count):
        quotes = self._load_quotes()
        if quotes is None:
            return None
        start_index = max(len(quotes) - count, 0) + 1
        return list(enumerate(quotes[-count:], start=start_index))

    def _delete_quote(self, quote_number):
        quotes = self._load_quotes()
        if quotes is None:
            return False

        index = quote_number - 1
        if index < 0 or index >= len(quotes):
            return None

        deleted_quote = quotes.pop(index)
        if not self._write_quotes(quotes):
            return False
        return deleted_quote

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

        quotes_path = self._quotes_path()
        line_num = 0
        selected_line = ""
        try:
            with quotes_path.open(encoding="utf-8") as quote_file:
                for line in quote_file:
                    if not line.strip():
                        continue
                    line_num += 1
                    if random.uniform(0, line_num) < 1:
                        selected_line = line
        except OSError as err:
            self.log.warning("OnJoin: failed to read %s: %s", quotes_path, err)
            return None
        return selected_line or None

    def addquote(self, irc, msg, args, text):
        """<text>

        Add a quote to the shared OnJoin quotes file.
        """

        quote = self._append_quote(text)
        if quote is None:
            irc.error("Quote cannot be blank.")
            return
        if quote is False:
            irc.error("Unable to update quotes file.")
            return

        irc.replySuccess()

    addquote = wrap(addquote, [("checkCapability", "admin"), "text"])

    def recentquotes(self, irc, msg, args, count):
        """[<count>]

        Show the most recent shared OnJoin quotes.
        """

        max_count = self.registryValue("maxRecentQuotes")
        quote_count = count or DEFAULT_RECENT_QUOTES
        quote_count = min(quote_count, max_count)

        quotes = self._recent_quotes(quote_count)
        if quotes is None:
            irc.error("Unable to read quotes file.")
            return
        if not quotes:
            irc.reply("No quotes are stored.")
            return

        for quote_number, quote in reversed(quotes):
            irc.reply(f"{quote_number}. {quote}", notice=True, private=True)

    recentquotes = wrap(
        recentquotes,
        [("checkCapability", "admin"), optional("positiveInt")],
    )

    def delquote(self, irc, msg, args, quote_number):
        """<quote_number>

        Delete a stored quote by its recentquotes number.
        """

        deleted_quote = self._delete_quote(quote_number)
        if deleted_quote is None:
            irc.error("No quote exists with that number.")
            return
        if deleted_quote is False:
            irc.error("Unable to update quotes file.")
            return

        irc.replySuccess()

    delquote = wrap(delquote, [("checkCapability", "admin"), "positiveInt"])

    def _teal(self, string):
        """Return a teal coloured string."""
        return utils.bold(utils.mircColor(string, "teal"))


Class = OnJoin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
