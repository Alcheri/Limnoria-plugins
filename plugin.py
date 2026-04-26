###
# Copyright © 2024, Barry KW Suridge
# All rights reserved.
#
###

# XXX Third-party modules
try:
    import aiohttp  # asynchronous HTTP client and server framework
    import asyncio  # asynchronous I/O
    import nest_asyncio  # allow nested event loops
except ImportError as ie:
    raise ImportError(f"Cannot import module: {ie}")

import re
import threading
import time
from urllib.parse import urlencode

import supybot.log as log
from supybot import callbacks
from supybot.commands import *
from supybot.i18n import PluginInternationalization

_ = PluginInternationalization("GoogleMaps")

nest_asyncio.apply()  # Allow nested asyncio event loops
REQUEST_TIMEOUT_SECONDS = 10
CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")
USAGE_MESSAGE = "Use --address, --reverse, or --directions."
MAP_OPTIONS = frozenset(("address", "reverse", "directions"))


# Global Error Routine
def handle_error(
    error: Exception, context: str = None, user_message: str = "An error occurred."
):
    """Log and handle errors gracefully."""
    message = user_message
    if user_message == "An error occurred." and error:
        message = str(error)
    raise callbacks.Error(message)


# Clean Output Utility
def clean_output(text: str) -> str:
    """Clean and simplify text output for user readability."""
    return CONTROL_CHARS_RE.sub(" ", str(text)).strip()


def validate_coordinates(user_input: str) -> str:
    """Validate and normalise a latitude,longitude pair."""
    try:
        latitude_text, longitude_text = map(str.strip, user_input.split(","))
        latitude = float(latitude_text)
        longitude = float(longitude_text)
    except (AttributeError, ValueError):
        raise ValueError(
            "Invalid format for reverse geocoding. Use: 'latitude,longitude'"
        )

    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError(
            "Invalid coordinates. Latitude must be -90 to 90 and longitude -180 to 180."
        )

    return f"{latitude:.6f},{longitude:.6f}"


def build_directions_url(origin: str, destination: str) -> str:
    """Build a Google Maps directions URL with encoded user input."""
    query = urlencode({"api": "1", "origin": origin, "destination": destination})
    return f"https://www.google.com/maps/dir/?{query}"


class CooldownTracker:
    """Track per-user command cooldowns."""

    def __init__(self):
        self._seen = {}
        self._lock = threading.Lock()

    def remaining(self, key, cooldown_seconds):
        if not cooldown_seconds:
            return 0

        now = time.monotonic()
        with self._lock:
            last_seen = self._seen.get(key)
            if last_seen is None or now - last_seen >= cooldown_seconds:
                self._seen[key] = now
                return 0
            return max(1, int(cooldown_seconds - (now - last_seen)))


class GoogleMaps(callbacks.Plugin):
    """
    Interact with the Google Maps API to retrieve map information based on user input.
    """

    threaded = False

    def __init__(self, irc):
        super().__init__(irc)
        self.irc = irc
        self.cooldowns = CooldownTracker()

    async def process_arguments(self, optlist: dict, user_input: str) -> dict:
        """Handle and process different argument-based requests."""
        if not MAP_OPTIONS.intersection(optlist):
            raise ValueError(f"Invalid option provided. {USAGE_MESSAGE}")

        apikey = self.registryValue("googlemapsAPI")
        if not apikey:
            raise ValueError("Google Maps API key is missing.")

        base_url = "https://maps.googleapis.com/maps/api/"
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            if "address" in optlist:
                url = f"{base_url}geocode/json"
                params = {"address": user_input, "key": apikey}
            elif "reverse" in optlist:
                latlng = validate_coordinates(user_input)

                url = f"{base_url}geocode/json"
                params = {"latlng": latlng, "key": apikey}
            elif "directions" in optlist:
                if not user_input or "|" not in user_input:
                    log.error(
                        "Invalid input format for directions. Expected format: 'origin|destination'"
                    )
                    raise ValueError(
                        "Invalid input format for directions. Use: 'origin|destination'"
                    )

                origin, destination = map(str.strip, user_input.split("|", 1))
                url = f"{base_url}directions/json"
                params = {"destination": destination, "origin": origin, "key": apikey}
            else:
                raise ValueError(f"Invalid option provided. {USAGE_MESSAGE}")

            async with session.get(url, params=params) as response:
                if response.status != 200:
                    handle_error(
                        Exception(f"API call failed with status {response.status}"),
                        "API Request",
                    )
                response_json = await response.json()
                return response_json

    @wrap(
        [getopts({"address": "", "reverse": "", "directions": ""}), additional("text")]
    )
    def map(self, irc, msg, args, optlist, user_input=None):
        """
        <text>
        Interact with the Google Maps API to retrieve map information based on user input.

        Args:
            irc: The IRC object.
            msg: The message object containing details about the message.
            args: Additional arguments.
            user_input: The text input provided by the user.

        Returns:
            None

        Example:
            @map --address 1600 Amphitheatre Parkway, Mountain View, CA
            @map --reverse -- -37.5321492, 143.8235249
            @map --directions Moscow | Vladivostok
        """
        if not self.registryValue("enabled", msg.channel, irc.network):
            return

        optlist = dict(optlist)
        log.info("Processing GoogleMaps request with options: %s", sorted(optlist))

        cooldown = self._cooldown_remaining(irc, msg)
        if cooldown:
            irc.error(
                f"Please wait {cooldown}s before sending another Google Maps request.",
                prefixNick=False,
            )
            return

        try:
            loop = asyncio.get_event_loop()
            data = loop.run_until_complete(self.process_arguments(optlist, user_input))

            if "directions" in optlist:
                if not data.get("routes"):
                    log.error("No routes found in the API response.")
                    irc.error(
                        "No routes found. Please check your input.", prefixNick=False
                    )
                    return

                route = data["routes"][0]
                leg = route["legs"][0]
                start_address = leg.get("start_address", "Unknown")
                end_address = leg.get("end_address", "Unknown")
                distance = leg["distance"].get("text", "Unknown")
                duration = leg["duration"].get("text", "Unknown")

                origin, destination = map(str.strip, user_input.split("|", 1))
                directions_url = build_directions_url(origin, destination)

                response = (
                    f"Route from \x02{start_address}\x02 to \x02{end_address}\x02:\n"
                    f"Distance: \x02{distance}\x02, Duration: \x02{duration}\x02.\n"
                    f"Directions: {directions_url}"
                )
                clean_response = clean_output(response)
                irc.reply(clean_response, prefixNick=False)
            elif "reverse" in optlist or "address" in optlist:
                if not data.get("results"):
                    log.error("No results found in the API response.")
                    irc.error(
                        "No results found for the provided input. Please double-check your input.",
                        prefixNick=False,
                    )
                    return

                result = data["results"][0]
                formatted_address = result.get("formatted_address", "Unknown location")
                location_type = result.get("types", [])
                geometry = result.get("geometry", {})
                location = geometry.get("location", {})
                lat = location.get("lat", "Unknown")
                lng = location.get("lng", "Unknown")
                place_id = result.get("place_id", "N/A")

                response = (
                    f"Location: \x02{formatted_address}\x02\n"
                    f"Coordinates: \x02{lat}, {lng}\x02\n"
                    f"Type: {', '.join(location_type)}\n"
                    f"Place ID: {place_id}"
                )
                clean_response = clean_output(response)
                irc.reply(clean_response, prefixNick=False)
            else:
                irc.error(
                    f"Invalid option provided. {USAGE_MESSAGE}",
                    prefixNick=False,
                )
        except ValueError as ve:
            log.error(f"Input validation error: {ve}")
            irc.error(str(ve), prefixNick=False)
        except Exception:
            log.exception("Unexpected GoogleMaps error.")
            irc.error(
                "An unexpected error occurred. Please check the logs.", prefixNick=False
            )

    def _cooldown_remaining(self, irc, msg):
        cooldown = self.registryValue("cooldownSeconds", msg.channel, irc.network)
        key = (irc.network, msg.channel, msg.prefix)
        return self.cooldowns.remaining(key, cooldown)


Class = GoogleMaps

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
