import unittest
import asyncio
from types import SimpleNamespace
from unittest.mock import patch, AsyncMock, MagicMock
from supybot.test import PluginTestCase as SupybotPluginTestCase

SupybotPluginTestCase.__test__ = False
from .plugin import (
    GoogleMaps,
    build_directions_url,
    clean_output,
    validate_coordinates,
    CooldownTracker,
)

# FILE: GoogleMaps/test.py


class TestGoogleMaps(SupybotPluginTestCase):
    __test__ = False

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

    def test_missing_map_option_returns_usage_error(self):
        with self.assertRaises(ValueError) as context:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                self.plugin.process_arguments(
                    {}, "1600 Amphitheatre Parkway, Mountain View, CA"
                )
            )

        self.assertEqual(
            str(context.exception),
            "Invalid option provided. Use --address, --reverse, or --directions.",
        )

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


class GoogleMapsUnitTestCase(unittest.TestCase):
    def test_clean_output_removes_control_characters(self):
        self.assertEqual(clean_output("Line\nwith\x02control"), "Line with control")

    def test_build_directions_url_encodes_user_input(self):
        result = build_directions_url("Sydney & CBD", "Bondi Beach #1")

        self.assertEqual(
            result,
            "https://www.google.com/maps/dir/?api=1&origin=Sydney+%26+CBD&destination=Bondi+Beach+%231",
        )

    def test_validate_coordinates_normalises_valid_input(self):
        self.assertEqual(
            validate_coordinates("-37.5321492, 143.8235249"),
            "-37.532149,143.823525",
        )

    def test_validate_coordinates_rejects_out_of_range_input(self):
        with self.assertRaises(ValueError):
            validate_coordinates("-137.5321492, 143.8235249")

    def test_cooldown_is_per_user(self):
        plugin = GoogleMaps.__new__(GoogleMaps)
        plugin.cooldowns = CooldownTracker()
        plugin.registryValue = lambda name, *args: 5
        irc = SimpleNamespace(network="testnet")
        msg = SimpleNamespace(channel="#test", prefix="nick!user@example")

        self.assertEqual(plugin._cooldown_remaining(irc, msg), 0)
        self.assertGreaterEqual(plugin._cooldown_remaining(irc, msg), 1)


if __name__ == "__main__":
    unittest.main()
