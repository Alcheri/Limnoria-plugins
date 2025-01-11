# -*- coding: utf-8 -*-cd Wikipedia
###
# Copyright © 2025, Barry Suridge
# All rights reserved.
#
# Credits: spline [https://github.com/andrewtryder] for the inspiration.
###

import unittest
from unittest.mock import patch, Mock
from Wikipedia.plugin import Wikipedia

# FILE: Wikipedia/test.py


class TestWikipediaPlugin(unittest.TestCase):
    @patch("Wikipedia.plugin.requests.get")
    def test_wiki_success(self, mock_get):
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "parse": {"text": {"*": "<p>This is a test Wikipedia entry.</p>"}}
        }
        mock_get.return_value = mock_response

        # Create an instance of the Wikipedia plugin
        plugin = Wikipedia()

        # Mock the irc.reply method
        irc = Mock()
        plugin.wiki(irc, None, None, "Test")

        # Assert that irc.reply was called with the expected output
        irc.reply.assert_called_once_with(
            "This is a test Wikipedia entry.", prefixNick=False
        )

    @patch("Wikipedia.plugin.requests.get")
    def test_wiki_exception(self, mock_get):
        # Mock an exception during the API request
        mock_get.side_effect = Exception("API request failed")

        # Create an instance of the Wikipedia plugin
        plugin = Wikipedia()

        # Mock the irc.error method
        irc = Mock()
        plugin.wiki(irc, None, None, "Test")

        # Assert that irc.error was called with the expected error message
        irc.error.assert_called_once_with("Error: API request failed", Raise=True)


if __name__ == "__main__":
    unittest.main()
