from __future__ import annotations

import threading


class RequestLimiter:
    """Process-wide request limiter for threaded Limnoria command handlers."""

    def __init__(self, max_concurrent: int):
        self._semaphore = threading.BoundedSemaphore(
            max(1, int(max_concurrent))
        )

    def acquire(self) -> bool:
        return self._semaphore.acquire(blocking=False)

    def release(self) -> None:
        self._semaphore.release()
