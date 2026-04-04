###
# Copyright (c) 2016 - 2026, Barry Suridge
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.registry as registry

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("OnJoin")
except:
    _ = lambda x: x


def configure(advanced):
    from supybot.questions import expect, anything, something, yn

    conf.registerPlugin("OnJoin", True)


OnJoin = conf.registerPlugin("OnJoin")

conf.registerChannelValue(
    OnJoin, "enable", registry.Boolean(False, """Should plugin work in this channel?""")
)

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
