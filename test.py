###
# Copyright © 2025, Barry Suridge
# All rights reserved.
#
# Credits: spline [https://github.com/andrewtryder] for the inspiration.
###

from supybot.test import *
from unittest.mock import MagicMock, patch


class WikipediaTestCase(PluginTestCase):
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


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
