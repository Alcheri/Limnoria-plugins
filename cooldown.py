# -*- coding: utf-8 -*-
###
# Asyncio Cooldown Manager
#
# Small module. Big responsibility.
# Controls per-context rate limiting to keep IRC sane and APIs protected.
#
# Designed to be simple, predictable, and difficult to misuse.
###

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class CooldownManager:
    """
    Per-context cooldown tracker.

    Keys must already be context-isolated (e.g. f"{channel}:{nick}").

    This manager is intentionally simple and dict-backed to match v1.1 behaviour,
    while removing global-dict access from the rest of the codebase.
    """

    _store: Dict[str, float] = field(default_factory=dict)

    def last_seen(self, context_key: str) -> float:
        """Return last timestamp for context, or 0.0 if never seen."""
        if not context_key:
            return 0.0
        return float(self._store.get(context_key, 0.0))

    def should_wait_message(
        self, context_key: str, now: float, cooldown_s: float
    ) -> str | None:
        """
        If still in cooldown, return the exact user-facing wait message.
        If allowed, return None.

        Behaviour matches your current logic:
          wait_time = int(cooldown - (now - last_time)) + 1
        """
        if not context_key:
            # Defensive: treat empty key as "allowed" but do not track.
            return None

        cd = float(cooldown_s)
        if cd <= 0:
            return None

        last_time = self.last_seen(context_key)
        delta = float(now) - last_time

        if delta < cd:
            wait_time = int(cd - delta) + 1
            return f"Please wait {wait_time}s before sending another request."

        return None

    def record(self, context_key: str, now: float) -> None:
        """Record a timestamp for the context."""
        if not context_key:
            return
        self._store[context_key] = float(now)

    def clear(self, context_key: str) -> None:
        """Clear cooldown for a specific context."""
        if not context_key:
            return
        self._store.pop(context_key, None)

    def clear_all(self) -> None:
        """Clear all cooldowns."""
        self._store.clear()
