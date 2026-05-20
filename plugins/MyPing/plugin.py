###
# Copyright (c) 2020 - 2026, Barry Suridge
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
import builtins
import ipaddress
import re
import subprocess  # nosec B404
import sys
import threading
import time

###
import supybot.ircutils as utils
import supybot.callbacks as callbacks
from supybot.commands import wrap

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("MyPing")
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module

    def _(text):
        return text


from .local.colour import red, teal

###############
#  FUNCTIONS  #
###############

special_chars = ("-", "[", "]", "\\", "`", "^", "{", "}", "_")
UNSAFE_CONTROL_CHARS_RE = re.compile(
    r"[\x00-\x01\x04-\x0e\x10-\x15\x17-\x1c\x1e\x7f]"
)
HOSTNAME_LABEL_RE = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$"
)
MAX_TARGET_LENGTH = 253
MAX_REPLY_LENGTH = 360
PING_TIMEOUT = 3.0


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


def _limit_text(value, max_length=MAX_REPLY_LENGTH):
    text = UNSAFE_CONTROL_CHARS_RE.sub("", str(value)).strip()
    if len(text) <= max_length:
        return text
    return f"{text[: max_length - 3]}..."


def _valid_hostname(host):
    if len(host) > MAX_TARGET_LENGTH:
        return False

    labels = host.rstrip(".").split(".")
    if builtins.any(not label or len(label) > 63 for label in labels):
        return False

    return builtins.all(HOSTNAME_LABEL_RE.match(label) for label in labels)


def _valid_ping_target(host):
    raw = (host or "").strip()
    target = UNSAFE_CONTROL_CHARS_RE.sub("", raw).strip()
    if not target:
        return False, "", "Please provide a host, nick, IPv4, or IPv6 target."

    if target != raw:
        return False, "", "Ping target contains invalid characters."

    if target.startswith("-"):
        return False, "", "Ping target must not start with '-'."

    if len(target) > MAX_TARGET_LENGTH:
        return False, "", "Ping target is too long."

    try:
        ipaddress.ip_address(target)
        return True, target, ""
    except ValueError:
        pass

    if _valid_hostname(target):
        return True, target, ""

    return False, "", "Ping target contains invalid characters."


def _elapsed_loss(output):
    lines = [line for line in output.splitlines() if line.strip()]
    try:
        loss = lines[-2].split(",")[2].split()[0]
        timing = lines[-1].split()[3].split("/")
        elapsed = int(float(timing[1]))
    except (IndexError, ValueError):
        return "Ping completed; timing details unavailable."

    elapsed_time = divmod(elapsed, 1000.0)

    return (
        f"Time elapsed: {teal(elapsed_time)} seconds/milliseconds "
        f"Packet Loss: {teal(loss)}"
    )


class MyPing(callbacks.Plugin):
    def __init__(self, irc):
        self.__parent = super(MyPing, self)
        self.__parent.__init__(irc)
        self._cooldowns = {}
        self._cooldown_lock = threading.Lock()

    threaded = True

    @wrap(["something"])
    def ping(self, irc, msg, args, host):
        """<hostmask> | Nick | IPv4 or IPv6>
        An alternative to Supybot's PING function.
        """
        channel = msg.args[0]

        # Check if we should be 'disabled' in a channel.
        # config channel #channel plugins.myping.enable True or False (or On or Off)
        if not self.registryValue("enable", channel):
            return

        if is_nick(host):  # Valid nick?
            nick = host
            try:
                userHostmask = irc.state.nickToHostmask(nick)
                # Returns the nick and host of a user hostmask.
                nick, _, host = utils.splitHostmask(userHostmask)
            except KeyError:
                pass

        is_valid, host, error = _valid_ping_target(host)
        if not is_valid:
            irc.error(error, prefixNick=False)
            return

        cooldown = self._cooldown_remaining(irc, msg, channel)
        if cooldown:
            irc.error(
                f"Please wait {cooldown}s before sending another ping request.",
                prefixNick=False,
            )
            return

        if sys.platform.startswith("win"):
            cmd = ["ping", "-n", "1", "-w", "1000", host]
        else:
            cmd = ["ping", "-c", "1", "-W", "1", host]
        try:
            reply = subprocess.check_output(  # nosec B603
                cmd, text=True, timeout=PING_TIMEOUT
            ).strip()
            elapsed_loss = _elapsed_loss(reply)
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            # Will print the command failed
            self._reply(irc, f"{red(host)} is Not Reachable")
        else:
            self._reply(irc, f"{red(host)} is Reachable ~ {elapsed_loss}")

    def _cooldown_remaining(self, irc, msg, channel):
        cooldown = self.registryValue("cooldownSeconds", channel)
        if not cooldown:
            return 0

        now = time.monotonic()
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

    def _reply(self, irc, text):
        irc.reply(_limit_text(text), prefixNick=False)


Class = MyPing
