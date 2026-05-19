import unittest

from ..config.runtime import _clamp_int


class ConfigRuntimeTestCase(unittest.TestCase):
    def test_clamp_int_bounds_values(self):
        self.assertEqual(_clamp_int(-1, 1, 10), 1)
        self.assertEqual(_clamp_int(99, 1, 10), 10)
        self.assertEqual(_clamp_int(5, 1, 10), 5)
