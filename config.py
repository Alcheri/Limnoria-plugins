###
# Copyright (c) 2020 - 2026, Barry Suridge
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.registry as registry

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("MyPing")
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified themself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn

    conf.registerPlugin("MyPing", True)


MyPing = conf.registerPlugin("MyPing")
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(MyPing, 'someConfigVariableName',
#     registry.Boolean(False, _("""Help for someConfigVariableName.""")))
conf.registerChannelValue(
    MyPing, "enable", registry.Boolean(False, """Should plugin work in this channel?""")
)

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
