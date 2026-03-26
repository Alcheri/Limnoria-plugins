###
# Copyright © MMXXIV, Barry Suridge
# All rights reserved.
#
#
###

from supybot.setup import plugin_setup

plugin_setup(
    "GoogleMaps",
    install_requires=[
        "aiohttp",
        "nest_asyncio",
    ],
)
