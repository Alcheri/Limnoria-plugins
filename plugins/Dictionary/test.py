###
# Copyright (c) 2026, Barry Suridge
# All rights reserved.
###

import unittest

from supybot.test import PluginTestCase

PluginTestCase.__test__ = False

try:
    from . import plugin
except ImportError:  # pragma: no cover - allows direct unittest execution.
    import plugin


class DictionaryTestCase(PluginTestCase):
    __test__ = False
    plugins = ("Dictionary",)


class DictionarySmokeTestCase(unittest.TestCase):
    def test_plugin_module_exports_class(self):
        self.assertTrue(hasattr(plugin, "Class"))


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
