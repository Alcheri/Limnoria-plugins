###
# Copyright (c) 2012-2014, spline
# Copyright © MMXXIV, Barry Suridge
# All rights reserved.
#
#
###

from supybot.test import *
import supybot.conf as conf
from unittest.mock import AsyncMock, patch


MOCK_JSON_WITH_DEFINITION = (
    '{"list": [{"definition": "A greeting", "example": "hello there", '
    '"thumbs_up": 5, "thumbs_down": 1}], "tags": ["greeting"]}'
)

MOCK_JSON_EMPTY_LIST = '{"list": []}'


class UrbanDictionaryTestCase(PluginTestCase):
    plugins = ("UrbanDictionary",)

    @patch("UrbanDictionary.plugin.UrbanDictionary._fetch_url", new_callable=AsyncMock)
    def testUrbanDictionary(self, mock_fetch_url):
        mock_fetch_url.return_value = MOCK_JSON_WITH_DEFINITION
        conf.supybot.plugins.UrbanDictionary.disableANSI.setValue("True")
        self.assertRegexp("urbandictionary hello", ":: A greeting")
        self.assertRegexp("urbandictionary spline", ":: A greeting")

    @patch("UrbanDictionary.plugin.UrbanDictionary._fetch_url", new_callable=AsyncMock)
    def testUrbanDictionaryNoDefinition(self, mock_fetch_url):
        mock_fetch_url.return_value = MOCK_JSON_EMPTY_LIST
        self.assertError("urbandictionary unknownterm")


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
