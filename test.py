from supybot.test import *
from .plugin import Asyncio

# FILE: Asyncio/test.py


class AsyncioTestCase(PluginTestCase):
    plugins = ('Asyncio',)

    def test_plugin_load(self):
        self.assertNotError('load Asyncio')

    def test_plugin_help(self):
        self.assertNotError('help Asyncio')

    def test_async_functionality(self):
        # Assuming there is an async function to test
        self.assertNotError('async_function')

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79: