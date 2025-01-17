###
# Copyright (c) 2025, Barry Suridge
# All rights reserved.
#
#
###

import re
import requests
import time

# XXX Third-party modules
try:
    from bs4 import BeautifulSoup
except ImportError as ie:
    raise Exception(f"Cannot import module: {ie}")

import supybot.ircutils as ircutils
from supybot import callbacks
from supybot.commands import *
from supybot.i18n import PluginInternationalization


_ = PluginInternationalization("URLtitle")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0"
}


class URLtitle(callbacks.Plugin):
    """
    Automatically detects URLs in messages and replies with the website title, with caching.
    """

    threaded = True

    def __init__(self, irc):
        self.__parent = super(URLtitle, self)
        self.__parent.__init__(irc)
        self.cache = {}  # Simple cache for storing URL titles

    def fetch_title(self, url):
        # Check the cache
        if url in self.cache:
            title, timestamp = self.cache[url]
            if time.time() - timestamp < 600:  # Cache expiration logic
                return title

        try:
            # Fetch the webpage
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()

            # Parse the HTML and extract the title
            soup = BeautifulSoup(response.text, "html.parser")
            title_tag = soup.find("title")

            if title_tag:
                formatted_title = f"{title_tag.get_text(strip=True)}"
            else:
                formatted_title = f"Title for {url}: No title found"

            # Update the cache
            self.cache[url] = (formatted_title, time.time())
            return formatted_title
        except Exception as e:
            self.log.error(f"{e}")
            return f"Error fetching {url}:"

    def doPrivmsg(self, irc, msg):
        """
        Triggered when a message is sent in a channel.
        """
        channel = msg.args[0]
        if not self.registryValue("enabled", channel, irc.network):
            return
        text = msg.args[1]

        # Regular expression to detect URLs
        url_pattern = r"(https?://\S+|www\.\S+)"
        urls = re.findall(url_pattern, text)

        if urls:
            for url in urls:
                # Add http if the URL does not include a scheme
                if not url.startswith(("http://", "https://")):
                    url = "http://" + url

                title = self.fetch_title(url)
                irc.reply(title, to=channel)


Class = URLtitle


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
