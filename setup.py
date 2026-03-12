###
# Copyright © MMXXIV, Barry Suridge
# All rights reserved.
#
#
###

from supybot.setup import plugin_setup

plugin_setup(
    "Wikipedia",
    install_requires=[
        "beautifulsoup4",
        "requests",
    ],
)
