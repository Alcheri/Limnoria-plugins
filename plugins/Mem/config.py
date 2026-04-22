###
# Copyright (c) 2026, Barry Suridge
# All rights reserved.
#
#
###

from supybot import conf

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("Mem")
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified themself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    conf.registerPlugin("Mem", True)


Mem = conf.registerPlugin("Mem")
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Mem, 'someConfigVariableName',
#     registry.Boolean(False, _("""Help for someConfigVariableName.""")))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
