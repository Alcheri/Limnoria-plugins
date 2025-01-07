import unittest
from unittest.mock import patch, MagicMock
from Wikipedia.plugin import Wikipedia


class WikipediaTestCase(unittest.TestCase):
    def setUp(self):
        self.plugin = Wikipedia(None)  # Initialize the plugin with a mock IRC object

    @patch('requests.get')
    def test_wiki_success(self, mock_get):
        """Test a successful Wikipedia lookup."""
        # Mock the Wikipedia API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'parse': {
                'text': {
                    '*': '<p>Harald "Bluetooth" Gormsson was a king of Denmark and Norway.</p>'
                }
            }
        }
        mock_get.return_value = mock_response

        # Mock the IRC and message objects
        irc = MagicMock()
        msg = MagicMock()
        msg.channel = '#testchannel'
        irc.network = 'TestNetwork'

        # Mock the reply function to capture plugin output
        def mock_reply(msg_text, *args, **kwargs):
            self.assertIn('Harald "Bluetooth" Gormsson was a king of Denmark and Norway.', msg_text)

        self.plugin.reply = mock_reply

        # Call the wiki function
        self.plugin.wiki(irc, msg, ['Harald Bluetooth'])


if __name__ == '__main__':
    unittest.main()
