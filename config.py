###
# Copyright © 2024, Barry Suridge
# All rights reserved.
#
#
###

from supybot import conf, registry

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("Asyncio")
except:

    _ = lambda x: x


def configure(advanced):

    from supybot.questions import expect, anything, something, yn

    conf.registerPlugin("Asyncio", True)


Asyncio = conf.registerPlugin("Asyncio")
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Dictionary, 'someConfigVariableName',
#     registry.Boolean(False, _("""Help for someConfigVariableName.""")))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
