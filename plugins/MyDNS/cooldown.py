###
# Copyright © 2016 - 2026, Barry Suridge
# All rights reserved.
###

import threading
import time


class CooldownTracker:
    """Track per-context command cooldowns."""

    def __init__(self):
        self._seen = {}
        self._lock = threading.Lock()

    def remaining(self, key, cooldown):
        if not cooldown:
            return 0

        now = time.monotonic()
        with self._lock:
            self._prune(now, cooldown)
            last_seen = self._seen.get(key)
            if last_seen is None or now - last_seen >= cooldown:
                self._seen[key] = now
                return 0
            return max(1, int(cooldown - (now - last_seen)))

    def _prune(self, now, cooldown):
        expired = [
            key
            for key, last_seen in self._seen.items()
            if now - last_seen >= cooldown
        ]
        for key in expired:
            del self._seen[key]
