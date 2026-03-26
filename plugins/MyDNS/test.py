###
# Copyright (c) 2026, Barry Suridge
# All rights reserved.
###

import unittest

from supybot.test import *


class MyDNSTestCase(PluginTestCase):
    plugins = ("MyDNS",)


class MyDNSSmokeTestCase(unittest.TestCase):
    def test_plugin_module_exports_class(self):
        from . import plugin

        self.assertTrue(hasattr(plugin, "Class"))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
