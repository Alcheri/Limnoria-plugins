###
# Copyright (c) MMXXIV, Barry Suridge
# All rights reserved.
#
#
###

from supybot.setup import plugin_setup

plugin_setup(
    'Asyncio',
    install_requires=[
        'aiohttp',
        'asyncio',
        'nest_asyncio',
        'openai',
        'python-dotenv',
        'tiktoken',
    ],
)
