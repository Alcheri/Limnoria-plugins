###
# Asyncio Cooldown Manager
#
# Small module. Big responsibility.
# Controls per-context rate limiting to keep IRC sane and APIs protected.
#
# Designed to be simple, predictable, and difficult to misuse.
###

from collections import OrderedDict

MAX_COOLDOWN_CONTEXTS = 512


class CooldownManager(object):
    """
    Per-context cooldown tracker.

    Behaviour matches v1.1 logic:
      - last_time defaults to 0
      - if delta < cooldown -> wait_time = int(cooldown - delta) + 1
      - record timestamp when allowed (record-before-API; defensive)
    """

    def __init__(self, max_contexts=MAX_COOLDOWN_CONTEXTS):
        self._store = OrderedDict()  # context_key -> last_time (float)
        self._max_contexts = max(1, int(max_contexts))

    def _prune(self):
        while len(self._store) > self._max_contexts:
            self._store.popitem(last=False)

    def should_wait_message(self, context_key, now, cooldown_s):
        if not context_key:
            return None

        cd = float(cooldown_s)
        if cd <= 0.0:
            return None

        last_time = float(self._store.get(context_key, 0.0))
        if context_key in self._store:
            self._store.move_to_end(context_key)
        delta = float(now) - last_time

        if delta < cd:
            wait_time = int(cd - delta) + 1
            return "Please wait {}s before sending another request.".format(
                wait_time
            )

        return None

    def record(self, context_key, now):
        if not context_key:
            return
        self._store[context_key] = float(now)
        self._store.move_to_end(context_key)
        self._prune()

    def clear(self, context_key):
        if not context_key:
            return
        self._store.pop(context_key, None)

    def clear_all(self):
        self._store.clear()


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
