###
# Copyright © 2016 - 2025, Barry Suridge
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import json  # JavaScript Object Notation
import socket  # Low-level networking interface

# XXX For Python 3.4 and later
# HTTP client for Python
try:
    import urllib3
except ImportError as e:
    raise ImportError(f"Cannot import module: {e}")

# URL handling module for python
from urllib.parse import urlparse

# Validate and categorize the IP address according to their types
# (IPv4 or IPv6)
import ipaddress

# mIRC colour codes
from .local.colour import bold, teal

from supybot.commands import *
from supybot import callbacks, log
import supybot.ircutils as utils

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("MyDNS")
except ImportError:
    _ = lambda x: x

###############
#  FUNCTIONS  #
###############

dns = bold(teal("DNS: "))
loc = bold(teal("LOC: "))

# XXX https://datatracker.ietf.org/doc/html/rfc2812#section-2.3.1
# fmt: off
special_chars = ('-', '[', ']', '\\', '`', '^', '{', '}', '_')
# fmt: on


def format_location(data, address):
    parts = []

    city = data.get("city")
    if city:
        parts.append(f"City: {city} ")

    region_name = data.get("region_name")
    if region_name:
        parts.append(f"State: {region_name} ")

    longitude = data.get("longitude")
    if longitude is not None:
        parts.append(f"Long: {longitude} ")

    latitude = data.get("latitude")
    if latitude is not None:
        parts.append(f"Lat: {latitude} ")

    country_code = data.get("country_code")
    if country_code:
        parts.append(f"Country Code: {country_code} ")

    country_name = data.get("country_name")
    if country_name:
        parts.append(f"Country: {country_name} ")

    # Prefer provider-supplied flag emoji, then fall back to country code.
    flag = ""
    if "location" in data and "country_flag_emoji" in data["location"]:
        flag = data["location"].get("country_flag_emoji") or ""
    if not flag and country_code:
        flag = country_code_to_flag(country_code)
    if flag:
        parts.append(f"{flag} ")

    zip_code = data.get("zip")
    if zip_code:
        parts.append(f" Post/Zip Code: {zip_code}")

    try:
        return "".join(parts)
    except TypeError:
        log.error("MyDNS: Could not resolve %s", address)
        raise callbacks.Error(f"Could not resolve {address}")


def is_nick(nick):
    """Checks to see if a nickname `nick` is valid.
    According to :rfc:`2812 #section-2.3.1`, section 2.3.1, a nickname must start
    with either a letter or one of the allowed special characters, and after
    that it may consist of any combination of letters, numbers, or allowed
    special characters.
    """
    if not nick:
        return False

    if not nick[0].isalpha() and nick[0] not in special_chars:
        return False
    for char in nick[1:]:
        if not char.isalnum() and char not in special_chars:
            return False
    return True


def is_ip(s):
    """Returns whether or not a given string is a
    valid IPv4 or IPv6 address.
    """
    try:
        ipaddress.ip_address(s)
        return True
    except ValueError:
        return False


def normalize_lookup_target(target):
    """Extract a host from raw input (hostname, URL, or host:port)."""
    value = (target or "").strip()
    if not value:
        return ""

    parsed = urlparse(value)
    if parsed.scheme:
        host = parsed.hostname or parsed.netloc
    elif "/" in value:
        parsed = urlparse(f"//{value}")
        host = parsed.hostname or parsed.netloc or value.split("/")[0]
    else:
        parsed = urlparse(f"//{value}")
        host = parsed.hostname or value

    return (host or "").strip("[]")


def pick_best_ip(addresses):
    """Prefer globally-routable IPs for more useful geolocation results."""
    valid = []
    for address in addresses:
        try:
            valid.append((address, ipaddress.ip_address(address)))
        except ValueError:
            continue

    if not valid:
        return addresses[0] if addresses else None

    for address, parsed in valid:
        if parsed.is_global:
            return address

    for address, parsed in valid:
        if not (parsed.is_loopback or parsed.is_link_local or parsed.is_unspecified):
            return address

    return valid[0][0]


def is_public_ip(address):
    try:
        return ipaddress.ip_address(address).is_global
    except ValueError:
        return False


def country_code_to_flag(country_code):
    if not country_code or len(country_code) != 2:
        return ""
    code = country_code.upper()
    if not code.isalpha():
        return ""
    return chr(127397 + ord(code[0])) + chr(127397 + ord(code[1]))


def score_geoip_result(data):
    """Score GeoIP quality so we can pick the most complete provider result."""
    score = 0
    for key in ("city", "region_name", "country_name", "country_code", "zip"):
        if data.get(key):
            score += 1

    if data.get("latitude") is not None:
        score += 2
    if data.get("longitude") is not None:
        score += 2

    return score


def normalize_geoip(source, payload):
    """Normalize provider responses to the format_location schema."""
    if source == "ipstack":
        return {
            "city": payload.get("city"),
            "region_name": payload.get("region_name"),
            "longitude": payload.get("longitude"),
            "latitude": payload.get("latitude"),
            "country_code": payload.get("country_code"),
            "country_name": payload.get("country_name"),
            "zip": payload.get("zip"),
            "location": {
                "country_flag_emoji": (
                    payload.get("location", {}).get("country_flag_emoji")
                    or country_code_to_flag(payload.get("country_code"))
                )
            },
            "_source": source,
        }

    if source == "ipapi":
        code = payload.get("country_code")
        return {
            "city": payload.get("city"),
            "region_name": payload.get("region"),
            "longitude": payload.get("longitude"),
            "latitude": payload.get("latitude"),
            "country_code": code,
            "country_name": payload.get("country_name"),
            "zip": payload.get("postal"),
            "location": {"country_flag_emoji": country_code_to_flag(code)},
            "_source": source,
        }

    if source == "ip-api":
        code = payload.get("countryCode")
        return {
            "city": payload.get("city"),
            "region_name": payload.get("regionName"),
            "longitude": payload.get("lon"),
            "latitude": payload.get("lat"),
            "country_code": code,
            "country_name": payload.get("country"),
            "zip": payload.get("zip"),
            "location": {"country_flag_emoji": country_code_to_flag(code)},
            "_source": source,
        }

    return {}


PROVIDER_ALIASES = {
    "ipstack": "ipstack",
    "ipapi": "ipapi",
    "ipapi.co": "ipapi",
    "ip-api": "ip-api",
    "ip_api": "ip-api",
    "ip-api.com": "ip-api",
}


class MyDNS(callbacks.Plugin):
    """An alternative to Supybot's DNS function."""

    def __init__(self, irc):
        self.__parent = super(MyDNS, self)
        self.__parent.__init__(irc)
        # Reuse the connection pool instead of creating one per request.
        self.http = urllib3.PoolManager()

    threaded = True

    ##############
    #    MAIN    #
    ##############

    @wrap(["text"])
    def dns(self, irc, msg, args, address):
        """<hostname | Nick | URL | IPv4 or IPv6>
        An alternative to Limnoria's DNS function.
        Returns the ip of <hostname | Nick | URL | ip or IPv6> or the reverse
        DNS hostname of <ip> using Python's socket library
        """
        # Check if we should be 'enabled' in a channel.
        # config channel #channel supybot.plugins.MyDNS.enable True or False (On or Off)
        if not self.registryValue("enable", msg.channel, irc.network):
            return

        self.log.info("MyDNS: running on %s/%s", irc.network, msg.channel)

        address = (address or "").strip()
        if not address:
            irc.error("Please provide a hostname, URL, nick, or IP.", prefixNick=False)
            return

        if is_ip(address):
            irc.reply(self.gethostbyaddr(address), prefixNick=False)
        elif is_nick(address):  # Valid nick?
            nick = address
            try:
                userHostmask = irc.state.nickToHostmask(nick)
                nick, _, host = utils.splitHostmask(
                    userHostmask
                )  # Returns the nick and host of a user hostmask.
                if is_ip(host):
                    irc.reply(self.gethostbyaddr(host), prefixNick=False)
                else:
                    irc.reply(self.getaddrinfo(host), prefixNick=False)
            except KeyError:
                # Could be a hostname that matches nick syntax.
                irc.reply(self.getaddrinfo(address), prefixNick=False)
        else:  # Neither IP or IRC user nick.
            irc.reply(self.getaddrinfo(address), prefixNick=False)

    def _request_json(self, uri, timeout=2.5):
        try:
            response = self.http.request(
                "GET",
                uri,
                timeout=timeout,
                headers={"Accept": "application/json", "User-Agent": "MyDNS/1.0"},
            )
        except Exception as err:
            self.log.warning("MyDNS: HTTP request failed for %s: %s", uri, err)
            return None

        if response.status != 200:
            return None

        try:
            return json.loads(response.data.decode("utf-8"))
        except (TypeError, ValueError):
            return None

    def _geoip_ipstack(self, address, apikey):
        for scheme in ("https", "http"):
            uri = f"{scheme}://api.ipstack.com/{address}?access_key={apikey}"
            payload = self._request_json(uri, timeout=3.0)
            if not payload:
                continue
            if payload.get("success") is False:
                continue
            return normalize_geoip("ipstack", payload)
        return None

    def _geoip_ipapi(self, address):
        uri = f"https://ipapi.co/{address}/json/"
        payload = self._request_json(uri, timeout=2.5)
        if not payload or payload.get("error"):
            return None
        return normalize_geoip("ipapi", payload)

    def _geoip_ip_api(self, address):
        fields = "status,message,country,countryCode,regionName,city,zip,lat,lon"
        uri = f"http://ip-api.com/json/{address}?fields={fields}"
        payload = self._request_json(uri, timeout=2.5)
        if not payload or payload.get("status") != "success":
            return None
        return normalize_geoip("ip-api", payload)

    def _get_provider_order(self):
        raw = self.registryValue("geoipProviderOrder")
        if not raw:
            return ["ipstack", "ipapi", "ip-api"]

        providers = []
        for item in raw.split(","):
            name = item.strip().lower()
            if not name:
                continue
            provider = PROVIDER_ALIASES.get(name)
            if provider and provider not in providers:
                providers.append(provider)

        if not providers:
            return ["ipstack", "ipapi", "ip-api"]

        return providers

    def getaddrinfo(self, host):
        """Get host information. Use returned IP address
        to find the (approximate) geolocation of the host.
        """
        host = normalize_lookup_target(host).lower()
        if not host:
            return "Could not resolve empty host."

        try:
            result = socket.getaddrinfo(host, None)
        except socket.error as err:  # Catch failed address lookup.
            self.log.error("MyDNS: Could not resolve  %s: %s", host, err)
            return f"Could not resolve {host}: {err}"

        addresses = [item[4][0] for item in result if item and item[4]]
        selected_ip = pick_best_ip(addresses)
        if not selected_ip:
            return f"Could not resolve {host}: no usable IP address found"

        geoip = self.geoip(selected_ip)

        return f"{dns}{host} resolves to [{selected_ip}] {loc}{geoip}"

    def gethostbyaddr(self, ip):
        """Do a reverse lookup for ip."""
        if not is_ip(ip):
            return self.getaddrinfo(ip)

        try:
            hostname, _, address = socket.gethostbyaddr(ip)
            hostname = hostname + " <> " + address[0]
            geoip = self.geoip(address[0])
            shortname = hostname.split(".")[0]
            return f"{dns} <{shortname}> [{hostname}] {loc} {geoip}"
        except socket.error as err:  # Catch failed address lookup.
            self.log.error("MyDNS: Could not resolve  %s: %s", ip, err)
            return f"Could not resolve {ip}: {err}"

    def geoip(self, address):
        """Search for the geolocation of IP addresses.
        Accuracy not guaranteed.
        """
        apikey = self.registryValue("ipstackAPI")

        if not is_public_ip(address):
            return "Non-public IP address (geolocation unavailable)."

        provider_order = self._get_provider_order()
        candidates = []

        for provider in provider_order:
            if provider == "ipstack":
                if not apikey:
                    continue
                result = self._geoip_ipstack(address, apikey)
            elif provider == "ipapi":
                result = self._geoip_ipapi(address)
            elif provider == "ip-api":
                result = self._geoip_ip_api(address)
            else:
                result = None

            if result:
                candidates.append(result)

        if not candidates:
            if apikey:
                return "GeoIP lookup failed."
            return (
                "GeoIP lookup failed. Configure plugins.MyDNS.ipstackAPI "
                "for improved provider coverage."
            )

        best = max(candidates, key=score_geoip_result)
        if score_geoip_result(best) == 0:
            return "GeoIP unavailable for this IP."

        return f"{format_location(best, address)}"


Class = MyDNS

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
