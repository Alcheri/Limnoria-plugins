###
# Copyright (c) 2014, spline
# Copyright © MMXXIV, Barry Suridge
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
###

# my libs
import json
import time
try:
    import pendulum
except Exception as ie:
    raise Exception(f"Cannot import module: {ie}")

# supybot libs
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.world as world
import supybot.conf as conf
import supybot.log as log

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization("WorldTime")
except ImportError:
    _ = lambda x: x

filename = conf.supybot.directories.data.dirize("WorldTime.json")

HEADERS = {
    "User-agent": "Mozilla/5.0 (compatible; Supybot/Limnoria %s; WorldTime plugin)"
    % conf.version
}

class WorldTime(callbacks.Plugin):
    """Add the help for "@plugin help WorldTime" here
    This should describe *how* to use this plugin."""

    threaded = True

    ###############################
    # DATABASE HANDLING FUNCTIONS #
    ###############################

    def __init__(self, irc):
        self.__parent = super(WorldTime, self)
        self.__parent.__init__(irc)
        self.db = {}
        self._loadDb()
        world.flushers.append(self._flushDb)

    def _loadDb(self):
        """Loads the (flatfile) database mapping ident@hosts to timezones."""

        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.db = json.load(f)
        except FileNotFoundError:
            log.info("WorldTime: Database file not found, initializing empty database.")
            self.db = {}
        except json.JSONDecodeError as e:
            log.warning(f"WorldTime: Error decoding JSON database: {e}")
        except Exception as e:
            log.warning(f"WorldTime: Unable to load database: {e}")

    def _flushDb(self):
        """Flushes the (flatfile) database mapping ident@hosts to timezones."""

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.db, f, indent=4)
        except Exception as e:
            log.warning(f"WorldTime: Unable to write database: {e}")

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
            log.info(f"WorldTime: ERROR: _converttz: {e}")

    ##############
    # GAPI STUFF #
    ##############

    def _getlatlng(self, location):
        api_key = self.registryValue("mapsAPIkey")
        location = utils.web.urlquote(location)
        url = (
            "https://maps.googleapis.com/maps/api/geocode/json?"
            "address=%s&key=%s"
            % (location, api_key)
        )

        try:
            response = utils.web.getUrl(url, headers=HEADERS)
        except utils.web.Error as e:
            log.debug(f"WorldTime: Error fetching URL: {e}")
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
                log.error(f"_getlatlng: Status not OK. Result: {result}")
        except Exception as e:
            log.error(f"_getlatlng: {e}")

    def _gettime(self, latlng):
        api_key = self.registryValue("mapsAPIkey")
        latlng = utils.web.urlquote(latlng)
        url = (
            "https://maps.googleapis.com/maps/api/timezone/json?location="
            f"{latlng}&sensor=false&timestamp={int(time.time())}&key={api_key}"
        )

        try:
            response = utils.web.getUrl(url, headers=HEADERS)
        except utils.web.Error as e:
            log.debug(f"WorldTime: Error fetching URL: {e}")
            return None

        try:
            result = json.loads(response.decode("utf-8"))
            if result["status"] == "OK":
                return result
            else:
                log.error(f"WorldTime: _gettime: Status not OK. Result: {result}")
        except Exception as e:
            log.info(f"WorldTime: _gettime: {e}")

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
        if not location:
            try:
                nick = opts.get("nick", None)
                if nick:
                    if nick in irc.state.nicksToHostmasks:
                        host = irc.state.nickToHostmask(nick)
                    else:
                        irc.error(f"Nickname '{nick}' not found in the bot's state.", prefixNick=False, Raise=True)
                        return
                else:
                    host = msg.prefix

                ih = host.split("!")[1]
                location = self.db.get(ih)
                if not location:
                    irc.error(
                        f"No location for {ircutils.bold('*!' + ih)} is set. "
                        "Use the 'set' command to set a location for your current hostmask, "
                        "or call 'worldtime' with <location> as an argument.", prefixNick=False,
                        Raise=True,
                    )
            except KeyError:
                irc.error(
                    "Unable to resolve nickname or hostmask. Ensure the nick is in the channel "
                    "or the bot has seen the user before.", prefixNick=False,
                    Raise=True,
                )

        # first, grab lat and long for user location
        gc = self._getlatlng(location)
        if not gc:
            irc.error(f"I could not find the location for: {location}.", prefixNick=False, Raise=True)

        # next, grab the localtime for that location w/lat+long
        ll = self._gettime(gc["ll"])
        if not ll:
            irc.error(f"I could not find the local timezone for: {location}.", prefixNick=False, Raise=True)

        # if we're here, we have localtime zone
        lt = self._converttz(msg, ll["timeZoneId"])
        if lt:
            s = f"{ircutils.bold(gc['place'])} :: Current local time is: {lt} ({ll['timeZoneName']})"
            if self.registryValue("disableANSI", msg.args[0]):
                s = ircutils.stripFormatting(s)
            irc.reply(s, prefixNick=False)
        else:
            irc.error("Something went wrong during conversion to timezone.", prefixNick=False, Raise=True)

    worldtime = wrap(worldtime, [getopts({"nick": "nick"}), additional("text")])

    def set(self, irc, msg, args, timezone):
        """<location>

        Sets the location for your current ident@host to <location>."""
        ih = msg.prefix.split("!")[1]
        self.db[ih] = timezone
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
            irc.error(f"No entry for {ircutils.bold('*!' + ih)} exists.", prefixNick=False, Raise=True)

Class = WorldTime

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
