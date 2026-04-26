###
# Copyright © 2016 - 2026, Barry Suridge
# All rights reserved.
###

import json

import urllib3

from .core import normalize_geoip, redact_uri


class GeoIPService:
    """HTTP client for GeoIP providers."""

    def __init__(self, logger):
        self.log = logger
        self.http = urllib3.PoolManager()

    def request_json(self, uri, timeout=2.5):
        try:
            response = self.http.request(
                "GET",
                uri,
                timeout=timeout,
                headers={"Accept": "application/json", "User-Agent": "MyDNS/1.0"},
            )
        except Exception as err:
            self.log.warning(
                "MyDNS: HTTP request failed for %s: %s", redact_uri(uri), err
            )
            return None

        if response.status != 200:
            return None

        try:
            return json.loads(response.data.decode("utf-8"))
        except (TypeError, ValueError):
            return None

    def ipstack(self, address, apikey):
        uri = f"https://api.ipstack.com/{address}?access_key={apikey}"
        payload = self.request_json(uri, timeout=3.0)
        if not payload or payload.get("success") is False:
            return None
        return normalize_geoip("ipstack", payload)

    def ipapi(self, address):
        uri = f"https://ipapi.co/{address}/json/"
        payload = self.request_json(uri, timeout=2.5)
        if not payload or payload.get("error"):
            return None
        return normalize_geoip("ipapi", payload)

    def ip_api(self, address):
        fields = "status,message,country,countryCode,regionName,city,zip,lat,lon"
        uri = f"http://ip-api.com/json/{address}?fields={fields}"
        payload = self.request_json(uri, timeout=2.5)
        if not payload or payload.get("status") != "success":
            return None
        return normalize_geoip("ip-api", payload)
