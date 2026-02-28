# -*- coding: utf-8 -*-
from supybot import conf, registry

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization("Asyncio")
except Exception:
    _ = lambda x: x


def configure(advanced):
    # Limnoria convention: keep this even if unused for now.
    from supybot.questions import expect, anything, something, yn  # noqa: F401
    conf.registerPlugin("Asyncio", True)


Asyncio = conf.registerPlugin("Asyncio")


# ----------------------------
# Global Plugin Configuration
# ----------------------------
conf.registerGlobalValue(
    Asyncio,
    "maxUserTokens",
    registry.Integer(512, _("Maximum number of user input tokens")),
)

conf.registerGlobalValue(
    Asyncio,
    "cooldownSeconds",
    registry.Integer(5, _("Seconds between user messages")),
)

conf.registerGlobalValue(
    Asyncio,
    "botnick",
    registry.String("Assistant", _("Bot nickname")),
)

# OpenAI handles English dialects only:
# American / British / Australian / Canadian
conf.registerGlobalValue(
    Asyncio,
    "language",
    registry.String("British", _("Language preference")),
)

conf.registerGlobalValue(
    Asyncio,
    "debugMode",
    registry.Boolean(False, _("Enable debug logging")),
)

conf.registerGlobalValue(
    Asyncio,
    "ircChunkSize",
    registry.Integer(350, _("Max characters per IRC reply chunk")),
)

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
