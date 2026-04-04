###
# Copyright © 2025, Barry Suridge
# All rights reserved.
#
# Credits: spline [https://github.com/andrewtryder] for the inspiration.
###

# supybot libs
from supybot.commands import wrap
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization

_ = PluginInternationalization("Wikipedia")

import requests

# XXX Third-party modules
try:
    from bs4 import BeautifulSoup
except ImportError as ie:
    raise ImportError(f"Cannot import module: {ie}")

HEADERS = {
    "User-Agent": "Limnoria-Wikipedia/1.0 (+https://github.com/andrewtryder/Wikipedia)"
}
REQUEST_TIMEOUT = 10


class Wikipedia(callbacks.Plugin):
    """
    Limnoria plugin for Wikipedia searching and fetching of documents.
    """

    threaded = True

    def __init__(self, irc):
        super().__init__(irc)

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

        # Normalize spacing without changing user-provided capitalization.
        subject = " ".join(subject.split())
        if not subject:
            irc.error("Please provide a topic to search.", Raise=True)
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
                error_message = data["error"].get("info", "Unknown error")
                irc.reply(
                    f"No result for '{subject}' on Wikipedia ({error_message}).",
                    prefixNick=False,
                )
                return

            raw_html = data.get("parse", {}).get("text", {}).get("*")
            if not raw_html:
                irc.reply(
                    f"No readable summary available for '{subject}'.",
                    prefixNick=False,
                )
                return

            soup = BeautifulSoup(raw_html, "html.parser")
            paragraphs = []

            for p in soup.find_all("p"):
                paragraph_text = p.get_text(" ", strip=True)
                if not paragraph_text:
                    continue
                if "may refer to:" in paragraph_text.lower():
                    irc.reply(
                        f"Disambiguation page found for '{subject}'. Please be more specific.",
                        prefixNick=False,
                    )
                    return
                paragraphs.append(paragraph_text)
                if len(paragraphs) >= 2:
                    break

        except requests.exceptions.RequestException as e:
            irc.error(f"Network error: {e}", Raise=True)
            return
        except (KeyError, TypeError, ValueError) as e:
            irc.error(f"Unable to parse Wikipedia response: {e}", Raise=True)
            return

        if not paragraphs:
            irc.reply(
                f"No summary text found for '{subject}'.",
                prefixNick=False,
            )
            return

        # Return a longer summary or truncate if too long
        summary = " ".join(paragraphs)
        if len(summary) > 300:
            summary = summary[:297] + "... (truncated)"
        irc.reply(summary, prefixNick=False)


Class = Wikipedia

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
