import unittest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from supybot.test import PluginTestCase
from .plugin import GoogleMaps

# FILE: GoogleMaps/test.py


class TestGoogleMaps(PluginTestCase):
    plugins = ("GoogleMaps",)

    def setUp(self):
        super().setUp()
        self.plugin = GoogleMaps(self.irc)

    def test_missing_api_key(self):
        with patch.object(self.plugin, "registryValue", return_value=None):
            with self.assertRaises(ValueError) as context:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(
                    self.plugin.process_arguments(
                        {}, "1600 Amphitheatre Parkway, Mountain View, CA"
                    )
                )
        self.assertEqual(str(context.exception), "Google Maps API key is missing.")

    @patch("aiohttp.ClientSession.get")
    def test_process_address(self, mock_get):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "results": [
                    {
                        "formatted_address": "1600 Amphitheatre Parkway, Mountain View, CA"
                    }
                ]
            }
        )
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_get.return_value = mock_context

        with patch.object(self.plugin, "registryValue", return_value="fake_api_key"):
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                self.plugin.process_arguments(
                    {"address": ""}, "1600 Amphitheatre Parkway, Mountain View, CA"
                )
            )
        self.assertIn("results", result)
        self.assertEqual(
            result["results"][0]["formatted_address"],
            "1600 Amphitheatre Parkway, Mountain View, CA",
        )

    @patch("aiohttp.ClientSession.get")
    def test_process_reverse_geocoding(self, mock_get):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"results": [{"formatted_address": "Some Location"}]}
        )
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_get.return_value = mock_context

        with patch.object(self.plugin, "registryValue", return_value="fake_api_key"):
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                self.plugin.process_arguments(
                    {"reverse": ""}, "-37.5321492, 143.8235249"
                )
            )
        self.assertIn("results", result)
        self.assertEqual(result["results"][0]["formatted_address"], "Some Location")

    @patch("aiohttp.ClientSession.get")
    def test_process_directions(self, mock_get):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "routes": [
                    {
                        "legs": [
                            {
                                "start_address": "Moscow",
                                "end_address": "Vladivostok",
                                "distance": {"text": "9000 km"},
                                "duration": {"text": "100 hours"},
                            }
                        ]
                    }
                ]
            }
        )
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_get.return_value = mock_context

        with patch.object(self.plugin, "registryValue", return_value="fake_api_key"):
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(
                self.plugin.process_arguments(
                    {"directions": ""}, "Moscow | Vladivostok"
                )
            )
        self.assertIn("routes", result)
        self.assertEqual(result["routes"][0]["legs"][0]["start_address"], "Moscow")
        self.assertEqual(result["routes"][0]["legs"][0]["end_address"], "Vladivostok")

    def test_invalid_reverse_geocoding_format(self):
        with patch.object(self.plugin, "registryValue", return_value="fake_api_key"):
            with self.assertRaises(ValueError) as context:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(
                    self.plugin.process_arguments({"reverse": ""}, "invalid_format")
                )
        self.assertEqual(
            str(context.exception),
            "Invalid format for reverse geocoding. Use: 'latitude,longitude'",
        )

    @patch("aiohttp.ClientSession.get")
    def test_api_call_failure(self, mock_get):
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="server error")
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_response
        mock_get.return_value = mock_context

        with patch.object(self.plugin, "registryValue", return_value="fake_api_key"):
            with self.assertRaises(Exception) as context:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(
                    self.plugin.process_arguments(
                        {"address": ""}, "1600 Amphitheatre Parkway, Mountain View, CA"
                    )
                )
        self.assertIn("API call failed with status 500", str(context.exception))


if __name__ == "__main__":
    unittest.main()
