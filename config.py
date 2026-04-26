###
# Copyright (c) 2016 - 2026, Barry Suridge
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.utils as utils
import supybot.registry as registry

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("MyDNS")
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

    conf.registerPlugin("MyDNS", True)


MyDNS = conf.registerPlugin("MyDNS")

# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(MyDNS, 'someConfigVariableName',
#     registry.Boolean(False, _("""Help for someConfigVariableName.""")))

conf.registerGroup(MyDNS, "apikeys")

conf.registerGlobalValue(
    MyDNS,
    "ipstackAPI",
    registry.String("", _("""Sets the API key for ipstack."""), private=True),
)
conf.registerGlobalValue(
    MyDNS,
    "geoipProviderOrder",
    registry.String(
        "ipstack,ipapi",
        _("""Comma-separated GeoIP provider order. Supported values: "
            "ipstack, ipapi, ip-api."""),
    ),
)
conf.registerGlobalValue(
    MyDNS,
    "allowInsecureGeoIP",
    registry.Boolean(
        False,
        _("""Allows plaintext GeoIP providers such as ip-api. Disabled by default."""),
    ),
)
conf.registerChannelValue(
    MyDNS,
    "cooldownSeconds",
    registry.NonNegativeInteger(
        5,
        _("""Sets the per-user DNS lookup cooldown for this channel, in seconds."""),
    ),
)
conf.registerChannelValue(
    MyDNS,
    "enable",
    registry.Boolean(False, _("""Should plugin work in this channel?""")),
)

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
