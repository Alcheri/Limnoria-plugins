###
# Copyright (c) 2024, Barry Suridge
# All rights reserved.
#
#
###

import supybot.conf as conf

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("Dictionary")
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    def _(text):
        return text


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified themself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    conf.registerPlugin("Dictionary", True)


Dictionary = conf.registerPlugin("Dictionary")
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Dictionary, 'someConfigVariableName',
#     registry.Boolean(False, _("""Help for someConfigVariableName.""")))


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
