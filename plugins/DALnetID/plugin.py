###
# Copyright (c) 2026, Barry Suridge
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

from supybot import callbacks, ircmsgs
from supybot.commands import wrap
from supybot.i18n import PluginInternationalization

from . import config as plugin_config

_ = PluginInternationalization("DALnetID")


def nickservIdentify(irc):
    """Identify to DALnet's NickServ"""
    password = plugin_config.DALnetID.nickservPassword()
    irc.queueMsg(
        ircmsgs.privmsg("NickServ@services.dal.net", "IDENTIFY %s" % password)
    )


class DALnetID(callbacks.Plugin):
    """A plugin to identify to DALnet's NickServ"""

    threaded = False

    def __init__(self, irc):
        """Initialise the plugin with the current IRC object."""
        self.__parent = super(DALnetID, self)
        self.__parent.__init__(irc)
        self.irc = irc

    @wrap([])
    def id(self, irc, msg, args):
        """takes no arguments

        Identify to DALnet's NickServ using the configured password.
        """
        irc.reply("Identifying to NickServ...")

        if not plugin_config.DALnetID.nickservPassword():
            irc.error("NickServ password is not configured.")
            return
        nickservIdentify(irc)

        irc.reply("The operation succeeded.")


Class = DALnetID

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
