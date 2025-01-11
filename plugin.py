###
# Copyright © 2025, Barry Suridge
# All rights reserved.
#
# Credits: spline [https://github.com/andrewtryder] for the inspiration.
###

# supybot libs
from supybot.commands import *
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization("Wikipedia")

import requests

# XXX Third-party modules
try:
    from bs4 import BeautifulSoup
except ImportError as ie:
    raise Exception(f"Cannot import module: {ie}")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0"
}


class Wikipedia(callbacks.Plugin):
    """
    Add the help for "@plugin help Wikipedia" here
    This should describe *how* to use this plugin.
    """

    threaded = True

    def __init__(self, irc):
        self.__parent = super(Wikipedia, self)
        self.__parent.__init__(irc)

    @wrap(["text"])
    def wiki(self, irc, msg, args, subject):
        """
        <subject>

        Retrieve and display the Wikipedia entry for a given topic.

        This function takes a topic as input, searches for the corresponding Wikipedia entry, and displays the summary of the entry.
        If the topic is not found, it provides a message indicating that no entry was found for the given topic.
        """

        # Check if the plugin is enabled in the channel
        if not self.registryValue("enabled", msg.channel, irc.network):
            return

        # Normalize the subject input
        subject = " ".join([word.capitalize() for word in subject.split()])

        url = "https://en.wikipedia.org/w/api.php"
        PARAMS = {
            "action": "parse",
            "page": subject,
            "lang": "en",
            "format": "json",
            "prop": "text",
            "redirects": 1,  # Follow redirects
        }

        try:
            response = requests.get(url, params=PARAMS, headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                error_message = data["error"].get("info", "Unknown error")
                irc.reply(
                    f"The page '{subject}' does not exist on Wikipedia. Please check your query or try a different topic.",
                    prefixNick=False,
                )
                return

            raw_html = data["parse"]["text"]["*"]
            soup = BeautifulSoup(raw_html, "html.parser")
            text = ""

            for p in soup.find_all("p"):
                if "may refer to:" in p.text:
                    irc.reply(
                        f"Disambiguation page found for '{subject}'. Please be more specific.",
                        prefixNick=False,
                    )
                    return
                text += p.text

        except requests.exceptions.RequestException as e:
            irc.error(f"Network error: {e}", Raise=True)
            return
        except Exception as e:
            irc.error(f"{e}", Raise=True)
            return

        # Return a longer summary or truncate if too long
        summary = ". ".join(text.strip().split(".")[:2]) + "."
        if len(summary) > 300:
            summary = summary[:297] + "... (truncated)"
        irc.reply(summary, prefixNick=False)


Class = Wikipedia

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
