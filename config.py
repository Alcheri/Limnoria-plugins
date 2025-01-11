###
# Copyright © 2025, Barry Suridge
# All rights reserved.
#
# Credits: spline [https://github.com/andrewtryder] for the inspiration.
###

from supybot import conf, registry

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("Asyncio")
except:
    _ = lambda x: x


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn

    conf.registerPlugin("Wikipedia", True)


Wikipedia = conf.registerPlugin("Wikipedia")

# XXX Default: False
conf.registerChannelValue(
    Wikipedia,
    "enabled",
    registry.Boolean(False, """Should plugin work in this channel?"""),
)

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=250:
