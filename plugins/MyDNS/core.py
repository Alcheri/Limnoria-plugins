###
# Copyright © 2016 - 2026, Barry Suridge
# All rights reserved.
###

import ipaddress
import re
from urllib.parse import urlparse

from supybot import callbacks, log

from .local.colour import bold, teal

dns = bold(teal("DNS: "))
loc = bold(teal("LOC: "))

# XXX https://datatracker.ietf.org/doc/html/rfc2812#section-2.3.1
# fmt: off
special_chars = ('-', '[', ']', '\\', '`', '^', '{', '}', '_')
# fmt: on

CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")


def sanitise_provider_text(value):
    """Remove IRC/control characters from provider-supplied text."""
    if value is None:
        return ""
    return CONTROL_CHARS_RE.sub("", str(value)).strip()


def format_coordinate(value):
    """Format latitude/longitude values for readable IRC output."""
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return sanitise_provider_text(value)


def redact_uri(uri):
    """Hide query strings before logging provider request URIs."""
    parsed = urlparse(uri)
    if not parsed.query:
        return uri
    return parsed._replace(query="<redacted>").geturl()


def format_location(data, address):
    parts = []

    city = data.get("city")
    if city:
        parts.append(f"City: {sanitise_provider_text(city)} ")

    region_name = data.get("region_name")
    if region_name:
        parts.append(f"State: {sanitise_provider_text(region_name)} ")

    longitude = data.get("longitude")
    if longitude is not None:
        parts.append(f"Long: {format_coordinate(longitude)} ")

    latitude = data.get("latitude")
    if latitude is not None:
        parts.append(f"Lat: {format_coordinate(latitude)} ")

    country_code = data.get("country_code")
    if country_code:
        parts.append(f"Country Code: {sanitise_provider_text(country_code)} ")

    country_name = data.get("country_name")
    if country_name:
        parts.append(f"Country: {sanitise_provider_text(country_name)} ")

    flag = ""
    if "location" in data and "country_flag_emoji" in data["location"]:
        flag = data["location"].get("country_flag_emoji") or ""
    if not flag and country_code:
        flag = country_code_to_flag(country_code)
    if flag:
        parts.append(f"{sanitise_provider_text(flag)} ")

    zip_code = data.get("zip")
    if zip_code:
        parts.append(f" Post/Zip Code: {sanitise_provider_text(zip_code)}")

    try:
        return "".join(parts)
    except TypeError:
        log.error("MyDNS: Could not resolve %s", address)
        raise callbacks.Error(f"Could not resolve {address}")


def is_nick(nick):
    """Return whether nick is a valid IRC nickname."""
    if not nick:
        return False

    if not nick[0].isalpha() and nick[0] not in special_chars:
        return False
    for char in nick[1:]:
        if not char.isalnum() and char not in special_chars:
            return False
    return True


def is_ip(s):
    """Return whether s is a valid IPv4 or IPv6 address."""
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
    """Normalise provider responses to the format_location schema."""
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


DEFAULT_PROVIDER_ORDER = ["ipstack", "ipapi"]
