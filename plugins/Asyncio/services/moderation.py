# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
import random
from functools import lru_cache

import supybot.log as log

from .openai_client import ensure_openai_client


@lru_cache(maxsize=512)
def _moderation_cache(text: str) -> bool:
    try:
        openai_client = ensure_openai_client()
        response = openai_client.moderations.create(
            model="omni-moderation-latest", input=text
        )
        return bool(response.results[0].flagged)
    except Exception as error:
        log.warning("[Asyncio] Moderation error (fail-open): {}".format(error))
        return False


async def check_moderation_flag(
    user_input: str,
    *,
    to_thread_fn=asyncio.to_thread,
    sleep_fn=asyncio.sleep,
    random_uniform_fn=random.uniform,
) -> bool:
    text = (user_input or "").strip()
    if not text or text.startswith("!") or len(text) < 5:
        return False

    delay = 1.0
    for _attempt in range(3):
        try:
            return await to_thread_fn(_moderation_cache, text)
        except Exception as error:
            message = str(error)
            if "429" in message or "Too Many Requests" in message:
                await sleep_fn(delay + random_uniform_fn(0, 0.5))
                delay *= 2
            else:
                log.error("[Asyncio] Moderation failure: {}".format(error))
                break

    return False


def clear_moderation_cache() -> None:
    _moderation_cache.cache_clear()
