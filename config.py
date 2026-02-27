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


# ----------------------------
# Plugin Config Registration
# ----------------------------
conf.registerGlobalValue(
    conf.supybot.plugins.Asyncio,
    "maxUserTokens",
    registry.Integer(512, "Maximum number of user input tokens"),
)

conf.registerGlobalValue(
    conf.supybot.plugins.Asyncio,
    "cooldownSeconds",
    registry.Integer(5, "Seconds between user messages"),
)

conf.registerGlobalValue(
    conf.supybot.plugins.Asyncio,
    "botnick",
    registry.String("Puss", "Bot nickname"),
)

# OpenAI handles English dialects only:
# American
# British
# Australian
# Canadian
conf.registerGlobalValue(
    conf.supybot.plugins.Asyncio,
    "language",
    registry.String("British", "Language preference"),
)

conf.registerGlobalValue(
    conf.supybot.plugins.Asyncio,
    "debugMode",
    registry.Boolean(False, "Enable debug logging"),
)

conf.registerGlobalValue(
    conf.supybot.plugins.Asyncio,
    "ircChunkSize",
    registry.Integer(350, "Max characters per IRC reply chunk"),
)

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
