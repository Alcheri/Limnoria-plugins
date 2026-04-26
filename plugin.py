###
# Copyright © 2016 - 2026, Barry Suridge
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

import socket

from supybot.commands import *
from supybot import callbacks
import supybot.ircutils as utils

from .cooldown import CooldownTracker
from .core import (
    DEFAULT_PROVIDER_ORDER,
    PROVIDER_ALIASES,
    dns,
    format_location,
    is_ip,
    is_nick,
    is_public_ip,
    loc,
    normalize_lookup_target,
    pick_best_ip,
    score_geoip_result,
)
from .services import GeoIPService

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("MyDNS")
except ImportError:
    _ = lambda x: x


class MyDNS(callbacks.Plugin):
    """An alternative to Supybot's DNS function."""

    def __init__(self, irc):
        self.__parent = super(MyDNS, self)
        self.__parent.__init__(irc)
        self.geoip_service = GeoIPService(self.log)
        self.cooldowns = CooldownTracker()

    threaded = True

    @wrap(["text"])
    def dns(self, irc, msg, args, address):
        """<hostname | Nick | URL | IPv4 or IPv6>
        An alternative to Limnoria's DNS function.
        Returns the IP of <hostname | Nick | URL | IP or IPv6> or the reverse
        DNS hostname of <IP> using Python's socket library.
        """
        if not self.registryValue("enable", msg.channel, irc.network):
            return

        self.log.info("MyDNS: running on %s/%s", irc.network, msg.channel)

        address = (address or "").strip()
        if not address:
            irc.error("Please provide a hostname, URL, nick, or IP.", prefixNick=False)
            return

        cooldown = self._cooldown_remaining(irc, msg)
        if cooldown:
            irc.error(
                f"Please wait {cooldown}s before sending another DNS request.",
                prefixNick=False,
            )
            return

        if is_ip(address):
            irc.reply(self.gethostbyaddr(address), prefixNick=False)
        elif is_nick(address):
            nick = address
            try:
                user_hostmask = irc.state.nickToHostmask(nick)
                nick, _, host = utils.splitHostmask(user_hostmask)
                if is_ip(host):
                    irc.reply(self.gethostbyaddr(host), prefixNick=False)
                else:
                    irc.reply(self.getaddrinfo(host), prefixNick=False)
            except KeyError:
                irc.reply(self.getaddrinfo(address), prefixNick=False)
        else:
            irc.reply(self.getaddrinfo(address), prefixNick=False)

    def _cooldown_remaining(self, irc, msg):
        cooldown = self.registryValue("cooldownSeconds", msg.channel, irc.network)
        key = (irc.network, msg.channel, msg.prefix)
        return self.cooldowns.remaining(key, cooldown)

    def _get_provider_order(self):
        raw = self.registryValue("geoipProviderOrder")
        if not raw:
            return DEFAULT_PROVIDER_ORDER

        providers = []
        for item in raw.split(","):
            name = item.strip().lower()
            if not name:
                continue
            provider = PROVIDER_ALIASES.get(name)
            if provider and provider not in providers:
                providers.append(provider)

        if not providers:
            return DEFAULT_PROVIDER_ORDER

        return providers

    def getaddrinfo(self, host):
        """Get host information and approximate geolocation."""
        host = normalize_lookup_target(host).lower()
        if not host:
            return "Could not resolve empty host."

        try:
            result = socket.getaddrinfo(host, None)
        except socket.error as err:
            self.log.error("MyDNS: Could not resolve  %s: %s", host, err)
            return f"Could not resolve {host}: {err}"

        addresses = [item[4][0] for item in result if item and item[4]]
        selected_ip = pick_best_ip(addresses)
        if not selected_ip:
            return f"Could not resolve {host}: no usable IP address found"

        geoip = self.geoip(selected_ip)

        return f"{dns}{host} resolves to [{selected_ip}] {loc}{geoip}"

    def gethostbyaddr(self, ip):
        """Do a reverse lookup for IP."""
        if not is_ip(ip):
            return self.getaddrinfo(ip)

        try:
            hostname, _, address = socket.gethostbyaddr(ip)
            hostname = hostname + " <> " + address[0]
            geoip = self.geoip(address[0])
            shortname = hostname.split(".")[0]
            return f"{dns} <{shortname}> [{hostname}] {loc} {geoip}"
        except socket.error as err:
            self.log.error("MyDNS: Could not resolve  %s: %s", ip, err)
            return f"Could not resolve {ip}: {err}"

    def geoip(self, address):
        """Search for the approximate geolocation of an IP address."""
        apikey = self.registryValue("ipstackAPI")

        if not is_public_ip(address):
            return "Non-public IP address (geolocation unavailable)."

        provider_order = self._get_provider_order()
        candidates = []

        for provider in provider_order:
            if provider == "ipstack":
                if not apikey:
                    continue
                result = self.geoip_service.ipstack(address, apikey)
            elif provider == "ipapi":
                result = self.geoip_service.ipapi(address)
            elif provider == "ip-api":
                if not self.registryValue("allowInsecureGeoIP"):
                    continue
                result = self.geoip_service.ip_api(address)
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
