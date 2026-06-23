###
# Copyright © 2025, Barry Suridge
# All rights reserved.
#
# Credits: spline [https://github.com/andrewtryder] for the inspiration.
###

import unittest
from unittest.mock import MagicMock, patch

import requests
import supybot.test as supytest

from bs4 import BeautifulSoup

from Wikipedia import plugin


class WikipediaTestCase(supytest.PluginTestCase):
    __test__ = False
    plugins = ("Wikipedia",)

    @patch("Wikipedia.plugin.Wikipedia.registryValue", return_value=True)
    @patch("Wikipedia.plugin.requests.get")
    def test_wiki_success(self, mock_get, _mock_registry_value):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "parse": {
                "text": {
                    "*": "<p>This is a test Wikipedia entry.</p>",
                }
            }
        }
        mock_get.return_value = mock_response

        self.assertResponse("wiki test", "This is a test Wikipedia entry.")

    @patch("Wikipedia.plugin.Wikipedia.registryValue", return_value=True)
    @patch("Wikipedia.plugin.requests.get")
    def test_wiki_disambiguation(self, mock_get, _mock_registry_value):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "parse": {
                "text": {
                    "*": "<p>Mercury may refer to:</p>",
                }
            }
        }
        mock_get.return_value = mock_response

        self.assertResponse(
            "wiki mercury",
            "Disambiguation page found for 'mercury'. Please be more specific.",
        )

    @patch("Wikipedia.plugin.Wikipedia.registryValue", return_value=True)
    @patch("Wikipedia.plugin.requests.get")
    def test_wiki_no_result_error(self, mock_get, _mock_registry_value):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "error": {
                "info": "missingtitle",
            }
        }
        mock_get.return_value = mock_response

        self.assertResponse(
            "wiki topicthatdoesnotexist",
            "No result for 'topicthatdoesnotexist' on Wikipedia (missingtitle).",
        )

    @patch("Wikipedia.plugin.Wikipedia.registryValue", return_value=True)
    @patch("Wikipedia.plugin.requests.get")
    def test_wiki_subject_too_long_is_rejected(
        self, mock_get, _mock_registry_value
    ):
        self.assertError(f"wiki {'a' * 121}")
        mock_get.assert_not_called()

    @patch("Wikipedia.plugin.Wikipedia.registryValue", return_value=True)
    @patch("Wikipedia.plugin.requests.get")
    def test_wiki_network_error_is_generic(
        self, mock_get, _mock_registry_value
    ):
        mock_get.side_effect = requests.exceptions.Timeout(
            "internal connection detail"
        )

        self.assertError("wiki test")


def test_clean_text_strips_formatting_control_chars_and_caps():
    unittest.TestCase().assertEqual(
        plugin._clean_text("\x02hello\x02\x00 world", limit=8),
        "hello...",
    )


def test_cooldown_is_per_user_and_channel():
    bot = plugin.Wikipedia(MagicMock())
    bot.registryValue = MagicMock(return_value=5)

    irc = MagicMock()
    irc.network = "testnet"
    msg = MagicMock()
    msg.channel = "#test"
    msg.prefix = "user!ident@example.test"

    testcase = unittest.TestCase()
    testcase.assertTrue(bot._check_cooldown(irc, msg))
    testcase.assertFalse(bot._check_cooldown(irc, msg))

    other_channel_msg = MagicMock()
    other_channel_msg.channel = "#other"
    other_channel_msg.prefix = msg.prefix

    testcase.assertTrue(bot._check_cooldown(irc, other_channel_msg))


def test_reply_does_not_pretruncate_before_limnoria_mores():
    bot = plugin.Wikipedia(MagicMock())
    irc = MagicMock()
    text = "x" * (plugin.MAX_REPLY_LENGTH + 50)

    bot._reply(irc, text)

    irc.reply.assert_called_once_with(text, prefixNick=False)


def test_extract_summary_ignores_sidebar_paragraphs():
    soup = BeautifulSoup(
        """
        <div class="mw-parser-output">
            <table class="sidebar">
                <tr><td><p>Condorcet methods Positional voting</p></td></tr>
            </table>
            <p><b>Instant-runoff voting</b> is a ranked voting method.</p>
            <p>It repeatedly eliminates candidates with the fewest votes.</p>
        </div>
        """,
        "html.parser",
    )

    paragraphs, is_disambiguation = plugin._extract_summary_paragraphs(soup)

    testcase = unittest.TestCase()
    testcase.assertFalse(is_disambiguation)
    testcase.assertEqual(
        paragraphs,
        [
            "Instant-runoff voting is a ranked voting method.",
            "It repeatedly eliminates candidates with the fewest votes.",
        ],
    )


def test_clear_more_cache_removes_requesting_nick_and_hostmask():
    bot = plugin.Wikipedia(MagicMock())
    irc = MagicMock()
    irc._mores = {
        "Tester": ["nick stale"],
        "ident@example.test": ["hostmask stale"],
        "Other": ["other stale"],
    }
    msg = MagicMock()
    msg.nick = "Tester"
    msg.prefix = "Tester!ident@example.test"

    bot._clear_more_cache(irc, msg)

    testcase = unittest.TestCase()
    testcase.assertNotIn("Tester", irc._mores)
    testcase.assertNotIn("ident@example.test", irc._mores)
    testcase.assertEqual(irc._mores["Other"], ["other stale"])


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
