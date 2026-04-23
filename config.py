###
# Copyright (c) 2026, Barry Suridge
# All rights reserved.
#
#
###

from supybot import conf, registry

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("MessagesLog")
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified themself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn

    conf.registerPlugin("MessagesLog", True)


MessagesLog = conf.registerPlugin("MessagesLog")
conf.registerGlobalValue(
    MessagesLog,
    "logFilePath",
    registry.String(
        "~/runbot/logs/messages.log",
        _("""Path to the messages.log file to read."""),
    ),
)

conf.registerGlobalValue(
    MessagesLog,
    "lineCount",
    registry.PositiveInteger(
        20,
        _("""Default number of lines to read from the end of the log file."""),
    ),
)

conf.registerGlobalValue(
    MessagesLog,
    "maxLineCount",
    registry.PositiveInteger(
        100,
        _("""Maximum allowed line count to return in a single request."""),
    ),
)


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
