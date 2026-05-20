###
# Copyright (c) 2016 - 2026, Barry Suridge
# All rights reserved.
###

import unittest
from unittest import mock
from types import SimpleNamespace

from supybot.test import PluginTestCase as SupybotPluginTestCase

SupybotPluginTestCase.__test__ = False


class MyDNSTestCase(SupybotPluginTestCase):
    __test__ = False

    plugins = ("MyDNS",)


class MyDNSSmokeTestCase(unittest.TestCase):
    def test_plugin_module_exports_class(self):
        from . import plugin

        self.assertTrue(hasattr(plugin, "Class"))

    def test_redact_uri_hides_query_string(self):
        from . import core

        uri = "https://api.ipstack.com/8.8.8.8?access_key=secret"

        self.assertEqual(
            core.redact_uri(uri),
            "https://api.ipstack.com/8.8.8.8?<redacted>",
        )
        self.assertNotIn("secret", core.redact_uri(uri))

    def test_format_location_sanitises_provider_text(self):
        from . import core

        data = {
            "city": "Mel\x02bourne",
            "region_name": "Vic\x03toria",
            "longitude": "-122.33039855957031",
            "latitude": 47.60150146484375,
            "country_code": "AU",
            "country_name": "Aus\x1ftralia",
        }

        result = core.format_location(data, "203.0.113.1")

        self.assertIn("City: Melbourne", result)
        self.assertIn("State: Victoria", result)
        self.assertIn("Long: -122.3304", result)
        self.assertIn("Lat: 47.6015", result)
        self.assertIn("Country: Australia", result)
        self.assertNotIn("-122.33039855957031", result)
        self.assertNotIn("47.60150146484375", result)
        self.assertNotIn("\x02", result)
        self.assertNotIn("\x03", result)
        self.assertNotIn("\x1f", result)

    def test_format_location_limits_provider_text(self):
        from . import core

        data = {"city": "A" * 200}

        result = core.format_location(data, "203.0.113.1")

        self.assertLessEqual(len(result), 90)
        self.assertIn("...", result)

    def test_limit_reply_caps_output(self):
        from . import core

        result = core.limit_reply("A" * 500)

        self.assertEqual(len(result), core.MAX_IRC_REPLY)
        self.assertTrue(result.endswith("..."))

    def test_getaddrinfo_rejects_invalid_host_before_dns_lookup(self):
        from . import plugin

        resolver = plugin.MyDNS.__new__(plugin.MyDNS)

        with mock.patch("socket.getaddrinfo") as getaddrinfo:
            result = resolver.getaddrinfo("bad host.example")

        self.assertIn("invalid characters", result)
        getaddrinfo.assert_not_called()

    def test_getaddrinfo_rejects_oversized_host_before_dns_lookup(self):
        from . import plugin

        resolver = plugin.MyDNS.__new__(plugin.MyDNS)
        host = "a" * 64 + ".example"

        with mock.patch("socket.getaddrinfo") as getaddrinfo:
            result = resolver.getaddrinfo(host)

        self.assertIn("invalid DNS label", result)
        getaddrinfo.assert_not_called()

    def test_ipstack_uses_https_only(self):
        from .services import GeoIPService

        service = GeoIPService.__new__(GeoIPService)
        seen = []

        def request_json(uri, timeout=2.5):
            seen.append(uri)
            return {"success": False}

        service.request_json = request_json

        self.assertIsNone(service.ipstack("8.8.8.8", "secret"))
        self.assertEqual(
            seen,
            ["https://api.ipstack.com/8.8.8.8?access_key=secret"],
        )

    def test_ip_api_is_disabled_by_default(self):
        from . import plugin

        resolver = plugin.MyDNS.__new__(plugin.MyDNS)

        def registry_value(name, *args):
            values = {
                "allowInsecureGeoIP": False,
                "geoipProviderOrder": "ip-api",
                "ipstackAPI": "",
            }
            return values[name]

        def insecure_provider(address):
            raise AssertionError("plaintext provider should not be called")

        resolver.registryValue = registry_value
        resolver.geoip_service = SimpleNamespace(ip_api=insecure_provider)

        self.assertIn("GeoIP lookup failed", resolver.geoip("8.8.8.8"))

    def test_cooldown_is_per_user(self):
        from . import plugin
        from .cooldown import CooldownTracker

        resolver = plugin.MyDNS.__new__(plugin.MyDNS)
        resolver.cooldowns = CooldownTracker()
        resolver.registryValue = lambda name, *args: 5

        irc = SimpleNamespace(network="testnet")
        msg = SimpleNamespace(channel="#test", prefix="nick!user@example")

        self.assertEqual(resolver._cooldown_remaining(irc, msg), 0)
        self.assertGreaterEqual(resolver._cooldown_remaining(irc, msg), 1)

    def test_cooldown_prunes_expired_entries(self):
        from .cooldown import CooldownTracker

        tracker = CooldownTracker()
        tracker._seen[("net", "#chan", "old!user@example")] = 1.0

        with mock.patch("time.monotonic", return_value=10.0):
            self.assertEqual(
                tracker.remaining(("net", "#chan", "new!user@example"), 5),
                0,
            )

        self.assertNotIn(("net", "#chan", "old!user@example"), tracker._seen)


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
