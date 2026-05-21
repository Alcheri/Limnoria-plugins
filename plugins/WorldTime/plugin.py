###
# Copyright (c) 2014, spline
# Copyright © MMXXIV, Barry Suridge
# All rights reserved.
###

# my libs
import json
import os
import re
import threading
import time

try:
    import pendulum
except ImportError as ie:
    raise ImportError(f"Cannot import module: {ie}")

# supybot libs
import supybot.utils as utils
from supybot.commands import additional, getopts, wrap
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.world as world
import supybot.conf as conf
import supybot.log as log

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("WorldTime")
except ImportError:

    def _(x):
        return x


filename = conf.supybot.directories.data.dirize("WorldTime.json")

HEADERS = {
    "User-Agent": "Limnoria-WorldTime/1.0 (Supybot/Limnoria %s; +https://github.com/andrewtryder/WorldTime)"
    % conf.version
}
REQUEST_TIMEOUT = 10
MAX_LOCATION_LENGTH = 120
MAX_REPLY_LENGTH = 500
DEFAULT_MAX_RESPONSE_BYTES = 262144
UNSAFE_CONTROL_CHARS_RE = re.compile(
    r"[\x00-\x01\x04-\x0e\x10-\x15\x17-\x1c\x1e\x7f]"
)
WHITESPACE_RE = re.compile(r"\s+")


class WorldTime(callbacks.Plugin):
    """Look up the current local time and timezone for any location.

    Uses the Google Geocoding and Time Zone APIs. Requires a Google
    Maps API key to be configured via 'config plugins.worldtime.mapsapikey'.
    Users can store their location with the 'set' command and then call
    'worldtime' without arguments."""

    threaded = True

    ###############################
    # DATABASE HANDLING FUNCTIONS #
    ###############################

    def __init__(self, irc):
        self.__parent = super(WorldTime, self)
        self.__parent.__init__(irc)
        self.db = {}
        self._cooldowns = {}
        self._cooldown_lock = threading.Lock()
        self._loadDb()
        world.flushers.append(self._flushDb)

    def _clean_text(self, value, max_length=None, preserve_formatting=True):
        text = str(value or "")
        if not preserve_formatting:
            text = ircutils.stripFormatting(text)
        text = UNSAFE_CONTROL_CHARS_RE.sub(" ", text)
        text = WHITESPACE_RE.sub(" ", text).strip()
        if max_length is not None and len(text) > max_length:
            return f"{text[: max(0, max_length - 3)].rstrip()}..."
        return text

    def _validate_location(self, location):
        raw = str(location or "").strip()
        cleaned = self._clean_text(
            raw,
            max_length=MAX_LOCATION_LENGTH,
            preserve_formatting=False,
        )
        if not cleaned:
            return False, "", "Please provide a location."
        if len(raw) > MAX_LOCATION_LENGTH:
            return False, "", "Location is too long."
        if cleaned != WHITESPACE_RE.sub(" ", raw).strip():
            return False, "", "Location contains invalid characters."
        return True, cleaned, ""

    def _max_response_bytes(self):
        try:
            value = int(self.registryValue("maxResponseBytes"))
        except (TypeError, ValueError):
            return DEFAULT_MAX_RESPONSE_BYTES
        return max(1024, min(value, DEFAULT_MAX_RESPONSE_BYTES))

    def _log_safe_text(self, value):
        return self._clean_text(
            value, max_length=120, preserve_formatting=False
        )

    def _api_status_text(self, result):
        status = self._log_safe_text(result.get("status", "UNKNOWN"))
        message = self._log_safe_text(result.get("error_message", ""))
        if message:
            return f"{status}: {message}"
        return status

    def _reply(self, irc, text):
        irc.reply(
            self._clean_text(text, max_length=MAX_REPLY_LENGTH),
            prefixNick=False,
        )

    def _error(self, irc, text, raise_error=True):
        irc.error(
            self._clean_text(text, max_length=MAX_REPLY_LENGTH),
            prefixNick=False,
            Raise=raise_error,
        )

    def _cooldown_remaining(self, irc, msg):
        channel = msg.args[0]
        cooldown = self.registryValue("cooldownSeconds", channel)
        if not cooldown:
            return 0

        now = time.monotonic()
        cooldown = max(0, int(cooldown))
        if cooldown <= 0:
            return 0

        key = (irc.network, channel, msg.prefix)
        with self._cooldown_lock:
            expired = [
                item
                for item, last_seen in self._cooldowns.items()
                if now - last_seen >= cooldown
            ]
            for item in expired:
                del self._cooldowns[item]

            last_seen = self._cooldowns.get(key)
            if last_seen is None or now - last_seen >= cooldown:
                self._cooldowns[key] = now
                return 0
            return max(1, int(cooldown - (now - last_seen)))

    def _store_location(self, hostmask, location):
        is_valid, location, error = self._validate_location(location)
        if not is_valid:
            return False, error

        ih = hostmask.split("!")[1]
        self.db[ih] = location
        return True, ""

    def _loadDb(self):
        """Loads the (flatfile) database mapping ident@hosts to timezones."""

        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.db = json.load(f)
        except FileNotFoundError:
            log.info(
                "WorldTime: Database file not found, initialising empty database."
            )
            self.db = {}
        except json.JSONDecodeError as e:
            log.warning(
                "WorldTime: Error decoding JSON database: %s",
                e.__class__.__name__,
            )
            self.db = {}
        except Exception as e:
            log.warning(
                "WorldTime: Unable to load database: %s", e.__class__.__name__
            )
            self.db = {}

    def _flushDb(self):
        """Flushes the (flatfile) database mapping ident@hosts to timezones."""

        try:
            tmp_filename = f"{filename}.tmp"
            with open(tmp_filename, "w", encoding="utf-8") as f:
                json.dump(self.db, f, indent=4)
                f.write("\n")
            os.replace(tmp_filename, filename)
        except Exception as e:
            log.warning(
                "WorldTime: Unable to write database: %s", e.__class__.__name__
            )

    def die(self):
        self._flushDb()
        world.flushers.remove(self._flushDb)
        self.__parent.die()

    ##################
    # TIME FUNCTIONS #
    ##################

    def _converttz(self, msg, outputTZ):
        """Convert current time to a readable string in a given timezone."""

        try:
            dt = pendulum.now(outputTZ)
            outstrf = self.registryValue("format", msg.args[0])
            return dt.strftime(outstrf)
        except Exception as e:
            log.info(
                "WorldTime: timezone conversion failed: %s",
                e.__class__.__name__,
            )

    ##############
    # GAPI STUFF #
    ##############

    def _getlatlng(self, location):
        api_key = self.registryValue("mapsAPIkey")
        location = utils.web.urlquote(location)
        url = (
            "https://maps.googleapis.com/maps/api/geocode/json?"
            "address=%s&key=%s" % (location, api_key)
        )

        try:
            response = utils.web.getUrl(
                url, headers=HEADERS, timeout=REQUEST_TIMEOUT
            )
        except utils.web.Error as e:
            log.debug(
                "WorldTime: geocode fetch failed: %s", e.__class__.__name__
            )
            return None

        if len(response) > self._max_response_bytes():
            log.warning("WorldTime: geocode response exceeded size limit.")
            return None

        try:
            result = json.loads(response.decode())
            if result["status"] == "OK":
                lat = str(result["results"][0]["geometry"]["location"]["lat"])
                lng = str(result["results"][0]["geometry"]["location"]["lng"])
                place = result["results"][0]["formatted_address"]
                ll = f"{lat},{lng}"
                return {"place": place, "ll": ll}
            else:
                log.error(
                    "WorldTime: geocode status not OK: %s",
                    self._api_status_text(result),
                )
        except (
            KeyError,
            IndexError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as e:
            log.error(
                "WorldTime: geocode parse failed: %s", e.__class__.__name__
            )

    def _gettime(self, latlng):
        api_key = self.registryValue("mapsAPIkey")
        latlng = utils.web.urlquote(latlng)
        url = (
            "https://maps.googleapis.com/maps/api/timezone/json?location="
            f"{latlng}&timestamp={int(time.time())}&key={api_key}"
        )

        try:
            response = utils.web.getUrl(
                url, headers=HEADERS, timeout=REQUEST_TIMEOUT
            )
        except utils.web.Error as e:
            log.debug(
                "WorldTime: timezone fetch failed: %s", e.__class__.__name__
            )
            return None

        if len(response) > self._max_response_bytes():
            log.warning("WorldTime: timezone response exceeded size limit.")
            return None

        try:
            result = json.loads(response.decode("utf-8"))
            if result["status"] == "OK":
                return result
            else:
                log.error(
                    "WorldTime: timezone status not OK: %s",
                    self._api_status_text(result),
                )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
            log.info(
                "WorldTime: timezone parse failed: %s", e.__class__.__name__
            )

    ###################
    # PUBLIC FUNCTION #
    ###################

    def worldtime(self, irc, msg, args, opts, location):
        """[--nick <nick>] [<location>]

        Query GAPIs for <location> and attempt to figure out local time. [<location>]
        is only required if you have not yet set a location for yourself using the 'set'
        command. If --nick is given, try looking up the location for <nick>.
        """
        opts = dict(opts)
        if not self.registryValue("mapsAPIkey"):
            self._error(
                irc,
                "No Google Maps API key configured. Set one with: "
                "config plugins.worldtime.mapsapikey <key>",
            )
            return

        cooldown = self._cooldown_remaining(irc, msg)
        if cooldown:
            self._error(
                irc,
                f"Please wait {cooldown}s before using worldtime again.",
            )
            return

        if not location:
            try:
                nick = opts.get("nick", None)
                if nick:
                    if nick in irc.state.nicksToHostmasks:
                        host = irc.state.nickToHostmask(nick)
                    else:
                        self._error(
                            irc,
                            f"Nickname '{nick}' not found in the bot's state.",
                        )
                        return
                else:
                    host = msg.prefix

                ih = host.split("!")[1]
                location = self.db.get(ih)
                if not location:
                    self._error(
                        irc,
                        f"No location for {ircutils.bold('*!' + ih)} is set. "
                        "Use the 'set' command to set a location for your current hostmask, "
                        "or call 'worldtime' with <location> as an argument.",
                    )
                    return
            except (KeyError, IndexError):
                self._error(
                    irc,
                    "Unable to resolve nickname or hostmask. Ensure the nick is in the channel "
                    "or the bot has seen the user before.",
                )
                return

        is_valid, location, error = self._validate_location(location)
        if not is_valid:
            self._error(irc, error)
            return

        # first, grab lat and long for user location
        gc = self._getlatlng(location)
        if not gc:
            self._error(
                irc,
                f"I could not find the location for: {location}.",
            )
            return

        # next, grab the localtime for that location w/lat+long
        ll = self._gettime(gc["ll"])
        if not ll:
            self._error(
                irc,
                f"I could not find the local timezone for: {location}.",
            )
            return

        # if we're here, we have localtime zone
        lt = self._converttz(msg, ll["timeZoneId"])
        if lt:
            place = self._clean_text(
                gc["place"], max_length=MAX_LOCATION_LENGTH
            )
            zone_name = self._clean_text(ll["timeZoneName"], max_length=80)
            s = (
                f"{ircutils.bold(place)} :: Current local time is: "
                f"{lt} ({zone_name})"
            )
            if self.registryValue("disableANSI", msg.args[0]):
                s = ircutils.stripFormatting(s)
            self._reply(irc, s)
        else:
            self._error(
                irc,
                "Something went wrong during conversion to timezone.",
            )

    worldtime = wrap(
        worldtime, [getopts({"nick": "nick"}), additional("text")]
    )

    def set(self, irc, msg, args, timezone):
        """<location>

        Sets the location for your current ident@host to <location>."""
        is_valid, error = self._store_location(msg.prefix, timezone)
        if not is_valid:
            self._error(irc, error)
            return

        irc.replySuccess()

    set = wrap(set, ["text"])

    def unset(self, irc, msg, args):
        """takes no arguments.

        Unsets the location for your current ident@host."""
        ih = msg.prefix.split("!")[1]
        try:
            del self.db[ih]
            irc.replySuccess()
        except KeyError:
            self._error(
                irc,
                f"No entry for {ircutils.bold('*!' + ih)} exists.",
            )


Class = WorldTime

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
