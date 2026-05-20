###
# Copyright (c) 2016 - 2026, Barry Suridge
# All rights reserved.
#

import os
import random
import re
import tempfile
import threading
from pathlib import Path

import supybot.ircutils as utils
import supybot.callbacks as callbacks
from supybot.commands import optional, wrap

DEFAULT_RECENT_QUOTES = 5
HARD_MAX_QUOTES = 2000
HARD_RECENT_QUOTES = 25
MAX_QUOTE_LENGTH = 360
CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")


class OnJoin(callbacks.Plugin):
    """Send a notice to all users entering a channel."""

    public = False

    def __init__(self, irc):
        super().__init__(irc)
        self._quote_lock = threading.Lock()

    def _quotes_path(self):
        return Path(__file__).with_name("quotes.txt")

    def _normalise_quote(self, text):
        quote = " ".join(str(text).splitlines()).strip()
        quote = CONTROL_CHARS_RE.sub("", quote).strip()
        if len(quote) > MAX_QUOTE_LENGTH:
            quote = f"{quote[: MAX_QUOTE_LENGTH - 3]}..."
        return quote or None

    def _max_stored_quotes(self):
        try:
            configured = self.registryValue("maxQuotes")
        except Exception:
            configured = HARD_MAX_QUOTES
        return min(max(configured, 1), HARD_MAX_QUOTES)

    def _quote_file_lock(self):
        if not hasattr(self, "_quote_lock"):
            self._quote_lock = threading.Lock()
        return self._quote_lock

    def _load_quotes(self):
        quotes_path = self._quotes_path()
        max_quotes = self._max_stored_quotes()
        quotes = []
        try:
            with quotes_path.open(encoding="utf-8") as quote_file:
                for line in quote_file:
                    quote = self._normalise_quote(line)
                    if quote is None:
                        continue
                    quotes.append(quote)
                    if len(quotes) > max_quotes:
                        quotes.pop(0)
        except OSError as err:
            self.log.warning("OnJoin: failed to read %s: %s", quotes_path, err)
            return None
        return quotes

    def _write_quotes(self, quotes):
        quotes_path = self._quotes_path()
        tmp_name = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                delete=False,
                dir=str(quotes_path.parent),
                encoding="utf-8",
            ) as quote_file:
                tmp_name = quote_file.name
                for quote in quotes:
                    normalised = self._normalise_quote(quote)
                    if normalised:
                        quote_file.write(f"{normalised}\n")
            os.replace(tmp_name, str(quotes_path))
        except OSError as err:
            self.log.warning(
                "OnJoin: failed to write %s: %s", quotes_path, err
            )
            if tmp_name:
                try:
                    os.unlink(tmp_name)
                except OSError:
                    pass
            return False
        return True

    def _append_quote(self, text):
        quote = self._normalise_quote(text)
        if quote is None:
            return None

        with self._quote_file_lock():
            quotes = self._load_quotes()
            if quotes is None:
                return False

            quotes.append(quote)
            max_quotes = self._max_stored_quotes()
            if len(quotes) > max_quotes:
                quotes = quotes[-max_quotes:]

            if not self._write_quotes(quotes):
                return False
        return quote

    def _recent_quotes(self, count):
        count = min(count, HARD_RECENT_QUOTES)
        quotes = self._load_quotes()
        if quotes is None:
            return None
        start_index = max(len(quotes) - count, 0) + 1
        return list(enumerate(quotes[-count:], start=start_index))

    def _delete_quote(self, quote_number):
        with self._quote_file_lock():
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
                    if random.uniform(0, line_num) < 1:  # nosec B311
                        selected_line = line
        except OSError as err:
            self.log.warning("OnJoin: failed to read %s: %s", quotes_path, err)
            return None
        return self._normalise_quote(selected_line) if selected_line else None

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
        quote_count = min(quote_count, max_count, HARD_RECENT_QUOTES)

        quotes = self._recent_quotes(quote_count)
        if quotes is None:
            irc.error("Unable to read quotes file.")
            return
        if not quotes:
            irc.reply("No quotes are stored.")
            return

        for quote_number, quote in reversed(quotes):
            irc.reply(
                self._normalise_quote(f"{quote_number}. {quote}"),
                notice=True,
                private=True,
            )

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
