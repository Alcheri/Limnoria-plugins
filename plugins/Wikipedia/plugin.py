###
# Copyright © 2025, Barry Suridge
# All rights reserved.
#
# Credits: spline [https://github.com/andrewtryder] for the inspiration.
###

import re
import threading
import time

import requests

import supybot.ircutils as ircutils
import supybot.log as log

# supybot libs
from supybot.commands import wrap
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization

# XXX Third-party modules
try:
    from bs4 import BeautifulSoup
except ImportError as ie:
    raise ImportError(f"Cannot import module: {ie}")

_ = PluginInternationalization("Wikipedia")

HEADERS = {
    "User-Agent": "Limnoria-Wikipedia/1.0 (+https://github.com/andrewtryder/Wikipedia)"
}
REQUEST_TIMEOUT = 10
MAX_SUBJECT_LENGTH = 120
MAX_REPLY_LENGTH = 360
MAX_SUMMARY_LENGTH = 1200
CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")
WHITESPACE_RE = re.compile(r"\s+")


def _clean_text(value, limit=None):
    text = ircutils.stripFormatting(str(value or ""))
    text = CONTROL_CHARS_RE.sub(" ", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    if limit is not None and len(text) > limit:
        return f"{text[: max(0, limit - 3)].rstrip()}..."
    return text


def _validate_subject(subject):
    cleaned = _clean_text(subject)
    if not cleaned:
        raise ValueError("Please provide a topic to search.")
    if len(cleaned) > MAX_SUBJECT_LENGTH:
        raise ValueError("Topic is too long.")
    return cleaned


def _log_safe_text(value):
    return _clean_text(value, limit=120) or "<empty>"


class Wikipedia(callbacks.Plugin):
    """
    Limnoria plugin for Wikipedia searching and fetching of documents.
    """

    threaded = True

    def __init__(self, irc):
        super().__init__(irc)
        self._cooldowns = {}
        self._cooldown_lock = threading.Lock()

    def _reply(self, irc, text):
        irc.reply(_clean_text(text), prefixNick=False)

    def _error(self, irc, text):
        irc.error(_clean_text(text, limit=MAX_REPLY_LENGTH), Raise=True)

    def _clear_more_cache(self, irc, msg):
        mores = getattr(irc, "_mores", None)
        if mores is None:
            return

        for key in self._more_cache_keys(msg):
            mores.pop(key, None)

    def _more_cache_keys(self, msg):
        keys = []
        nick = getattr(msg, "nick", None)
        if nick:
            keys.append(nick)

        prefix = getattr(msg, "prefix", None) or ""
        if "!" in prefix and "@" in prefix:
            keys.append(prefix.split("!", 1)[1])

        return keys

    def _cooldown_key(self, irc, msg):
        channel = getattr(msg, "channel", None) or "PM"
        user = getattr(msg, "prefix", None) or "unknown"
        return (getattr(irc, "network", ""), channel, user)

    def _check_cooldown(self, irc, msg):
        cooldown_seconds = int(self.registryValue("cooldownSeconds") or 0)
        if cooldown_seconds <= 0:
            return True

        key = self._cooldown_key(irc, msg)
        now = time.monotonic()
        with self._cooldown_lock:
            expires_at = self._cooldowns.get(key, 0.0)
            if expires_at > now:
                remaining = int(expires_at - now) + 1
                self._error(
                    irc,
                    f"Please wait {remaining} seconds before using wiki again.",
                )
                return False
            self._cooldowns[key] = now + cooldown_seconds
        return True

    @wrap(["text"])
    def wiki(self, irc, msg, args, subject):
        """
        <subject>

        Retrieve and display the Wikipedia entry for a given topic.

        This function takes a topic as input, searches for the corresponding Wikipedia entry, and displays the summary of the entry.
        If the topic is not found, it provides a message indicating that no entry was found for the given topic.
        """

        # Only enforce channel enablement in channels; allow PM usage.
        channel = getattr(msg, "channel", None)
        if channel and not self.registryValue("enabled", channel, irc.network):
            return

        self._clear_more_cache(irc, msg)

        try:
            subject = _validate_subject(subject)
        except ValueError as e:
            self._error(irc, str(e))
            return

        if not self._check_cooldown(irc, msg):
            return

        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "parse",
            "page": subject,
            "lang": "en",
            "format": "json",
            "prop": "text",
            "redirects": 1,  # Follow redirects
        }

        try:
            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                error_message = _clean_text(
                    data["error"].get("info", "Unknown error"), limit=120
                )
                self._reply(
                    irc,
                    f"No result for '{subject}' on Wikipedia ({error_message}).",
                )
                return

            raw_html = data.get("parse", {}).get("text", {}).get("*")
            if not raw_html:
                self._reply(
                    irc,
                    f"No readable summary available for '{subject}'.",
                )
                return

            soup = BeautifulSoup(raw_html, "html.parser")
            paragraphs = []

            for p in soup.find_all("p"):
                paragraph_text = _clean_text(p.get_text(" ", strip=True))
                if not paragraph_text:
                    continue
                if "may refer to:" in paragraph_text.lower():
                    self._reply(
                        irc,
                        f"Disambiguation page found for '{subject}'. Please be more specific.",
                    )
                    return
                paragraphs.append(paragraph_text)
                if len(paragraphs) >= 2:
                    break

        except requests.exceptions.RequestException as e:
            log.warning(
                "Wikipedia request failed for %s: %s",
                _log_safe_text(subject),
                e.__class__.__name__,
            )
            self._error(irc, "Wikipedia request failed.")
            return
        except (KeyError, TypeError, ValueError) as e:
            log.warning(
                "Wikipedia response parse failed for %s: %s",
                _log_safe_text(subject),
                e.__class__.__name__,
            )
            self._error(irc, "Unable to parse Wikipedia response.")
            return

        if not paragraphs:
            self._reply(
                irc,
                f"No summary text found for '{subject}'.",
            )
            return

        # Return a longer summary or truncate if too long
        summary = _clean_text(" ".join(paragraphs), limit=MAX_SUMMARY_LENGTH)
        self._reply(irc, summary)


Class = Wikipedia

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79: autoindent:
