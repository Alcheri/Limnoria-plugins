###
# Copyright © 2024, Barry KW Suridge
# All rights reserved.
#
#
###

from supybot import conf, registry

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("GoogleMaps")
except:
    _ = lambda x: x


def configure(advanced):
    from supybot.questions import expect, anything, something, yn

    conf.registerPlugin("GoogleMaps", True)


GoogleMaps = conf.registerPlugin("GoogleMaps")

conf.registerGlobalValue(
    GoogleMaps,
    "googlemapsAPI",
    registry.String("", _("""Sets the API key for Google Maps."""), private=True),
)

conf.registerChannelValue(
    GoogleMaps,
    "enabled",
    registry.Boolean(False, """Should plugin work in this channel?"""),
)

conf.registerChannelValue(
    GoogleMaps,
    "cooldownSeconds",
    registry.NonNegativeInteger(
        5,
        _(
            """Sets the per-user Google Maps lookup cooldown for this channel, in seconds."""
        ),
    ),
)

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
