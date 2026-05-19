import unittest

from ..core.limits import RequestLimiter


class CoreLimitsTestCase(unittest.TestCase):
    def test_request_limiter_blocks_after_capacity(self):
        limiter = RequestLimiter(max_concurrent=1)

        self.assertTrue(limiter.acquire())
        self.assertFalse(limiter.acquire())

        limiter.release()
        self.assertTrue(limiter.acquire())
        limiter.release()
