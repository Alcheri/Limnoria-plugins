###
# Copyright (c) 2014, spline
# Copyright © MMXXIV, Barry Suridge
# All rights reserved.
###

import supybot.conf as conf
import supybot.registry as registry

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("WorldTime")
except ImportError:

    def _(text):
        return text


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified themself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    conf.registerPlugin("WorldTime", True)


WorldTime = conf.registerPlugin("WorldTime")
# This is where your configuration variables (if any) should go.  For example:
conf.registerChannelValue(
    WorldTime,
    "disableANSI",
    registry.Boolean(
        False, _("""Disable color/bolding for WorldTime output in channel.""")
    ),
)
conf.registerChannelValue(
    WorldTime,
    "format",
    registry.String(
        "%a, %H:%M",
        _(
            """Sets the output time format (using an strftime-formatted string)."""
        ),
    ),
)
conf.registerGlobalValue(
    WorldTime,
    "mapsAPIkey",
    registry.String(
        "", """Sets the Google Maps Places API key""", private=True
    ),
)

conf.registerChannelValue(
    WorldTime,
    "cooldownSeconds",
    registry.NonNegativeInteger(
        5,
        _("""Sets the per-user worldtime lookup cooldown in seconds."""),
    ),
)

conf.registerGlobalValue(
    WorldTime,
    "maxResponseBytes",
    registry.PositiveInteger(
        262144,
        _("""Maximum Google API response size to read, in bytes."""),
    ),
)

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
