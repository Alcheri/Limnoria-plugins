###
# Copyright (c) 2026, Barry Suridge
# All rights reserved.
###

import json
import unittest
from unittest import mock

from supybot.test import PluginTestCase

PluginTestCase.__test__ = False

try:
    from . import plugin
except ImportError:  # pragma: no cover - allows direct unittest execution.
    import plugin


class DictionaryTestCase(PluginTestCase):
    __test__ = False
    plugins = ("Dictionary",)


class DictionarySmokeTestCase(unittest.TestCase):
    def test_plugin_module_exports_class(self):
        self.assertTrue(hasattr(plugin, "Class"))

    def test_dict_rejects_overlong_lookup_before_network_request(self):
        dictionary = object.__new__(plugin.Dictionary)
        dictionary.log = mock.Mock()
        irc = mock.Mock()
        msg = mock.Mock(prefix="user!ident@host")

        with mock.patch.object(plugin.utils.web, "getUrl") as get_url:
            plugin.Dictionary.dict(
                dictionary,
                irc,
                msg,
                ["x" * (plugin.MAX_LOOKUP_LENGTH + 1)],
            )

        get_url.assert_not_called()
        irc.error.assert_called_once_with(
            "Lookup text is too long.", prefixNick=False
        )

    def test_dict_cleans_and_truncates_api_definition(self):
        dictionary = object.__new__(plugin.Dictionary)
        dictionary.log = mock.Mock()
        irc = mock.Mock()
        msg = mock.Mock(prefix="user!ident@host")
        raw_definition = "A definition\nwith control \x02characters. " + (
            "word " * 120
        )
        payload = json.dumps(
            [
                {
                    "meanings": [
                        {
                            "partOfSpeech": "noun",
                            "definitions": [{"definition": raw_definition}],
                        }
                    ]
                }
            ]
        ).encode("utf-8")

        with mock.patch.object(
            plugin.utils.web, "getUrl", return_value=payload
        ):
            plugin.Dictionary.dict(dictionary, irc, msg, ["example"])

        response = irc.reply.call_args.args[0]
        self.assertLessEqual(len(response), plugin.MAX_REPLY_LENGTH)
        self.assertNotIn("\n", response)
        self.assertNotIn("\x02", response)
        self.assertTrue(response.endswith("..."))


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
