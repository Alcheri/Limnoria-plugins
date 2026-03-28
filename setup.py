###
# Copyright (c) MMXXIV, Barry Suridge
# All rights reserved.
#
#
###

from supybot.setup import plugin_setup

plugin_setup(
    "Asyncio",
    install_requires=[
        "openai",
        "python-dotenv",
    ],
)
