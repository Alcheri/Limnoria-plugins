###
# Copyright (c) 2026, Barry Suridge
# All rights reserved.
###

import unittest

from supybot.test import PluginTestCase

from .tests.test_config_runtime import ConfigRuntimeTestCase
from .tests.test_cooldown import CooldownManagerTestCase
from .tests.test_core_chat import CoreChatTestCase
from .tests.test_core_limits import CoreLimitsTestCase
from .tests.test_core_text import CoreTextTestCase
from .tests.test_services_moderation import ServicesModerationTestCase
from .tests.test_services_openai_client import (
    ServicesOpenAIClientTestCase,
)
from .tests.test_state_memory import StateMemoryTestCase

__all__ = [
    "AsyncioTestCase",
    "AsyncioSmokeTestCase",
    "ConfigRuntimeTestCase",
    "CooldownManagerTestCase",
    "CoreChatTestCase",
    "CoreLimitsTestCase",
    "CoreTextTestCase",
    "ServicesModerationTestCase",
    "ServicesOpenAIClientTestCase",
    "StateMemoryTestCase",
]


class AsyncioTestCase(PluginTestCase):
    plugins = ("Asyncio",)


class AsyncioSmokeTestCase(unittest.TestCase):
    def test_plugin_module_exports_class(self):
        from . import plugin

        self.assertTrue(hasattr(plugin, "Class"))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
