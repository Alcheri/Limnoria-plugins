import unittest

from ..cooldown import CooldownManager


class CooldownManagerTestCase(unittest.TestCase):
    def test_record_prunes_old_contexts(self):
        cooldowns = CooldownManager(max_contexts=2)

        cooldowns.record("ctx-1", 1.0)
        cooldowns.record("ctx-2", 2.0)
        cooldowns.record("ctx-3", 3.0)

        self.assertIsNone(cooldowns.should_wait_message("ctx-1", 10.0, 5))
        self.assertIn(
            "Please wait", cooldowns.should_wait_message("ctx-2", 4.0, 5)
        )
        self.assertIn(
            "Please wait", cooldowns.should_wait_message("ctx-3", 4.0, 5)
        )
