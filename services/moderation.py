from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import supybot.log as log

from .openai_client import ensure_openai_client


@dataclass(frozen=True)
class ModerationResult:
    flagged: bool
    categories: tuple[str, ...] = ()
    request_id: str | None = None


def _get_flagged_categories(result: Any) -> tuple[str, ...]:
    categories = getattr(result, "categories", None)
    if categories is None:
        return ()

    model_dump = getattr(categories, "model_dump", None)
    if callable(model_dump):
        values = model_dump()
    elif isinstance(categories, dict):
        values = categories
    else:
        values = vars(categories)

    if not isinstance(values, dict):
        return ()

    return tuple(
        sorted(name for name, value in values.items() if value is True)
    )


def _get_moderation_result(response: Any) -> ModerationResult:
    result = response.results[0]
    request_id = getattr(response, "_request_id", None)
    if not isinstance(request_id, str):
        request_id = None

    return ModerationResult(
        flagged=bool(result.flagged),
        categories=_get_flagged_categories(result),
        request_id=request_id,
    )


@lru_cache(maxsize=512)
def _moderation_cache(text: str) -> ModerationResult:
    openai_client = ensure_openai_client()
    response = openai_client.moderations.create(
        model="omni-moderation-latest", input=text
    )
    return _get_moderation_result(response)


async def check_moderation_flag(
    user_input: str,
    *,
    context_key: str | None = None,
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
            moderation_result = await to_thread_fn(_moderation_cache, text)
            if isinstance(moderation_result, bool):
                return moderation_result

            if moderation_result.flagged:
                categories = (
                    ", ".join(moderation_result.categories) or "unknown"
                )
                request_id = moderation_result.request_id or "unknown"
                log.warning(
                    "[Asyncio] Moderation blocked request for {}: "
                    "categories={}, request_id={}".format(
                        context_key or "unknown",
                        categories,
                        request_id,
                    )
                )
            return moderation_result.flagged
        except Exception as error:
            message = str(error)
            if "429" in message or "Too Many Requests" in message:
                await sleep_fn(delay + random_uniform_fn(0, 0.5))
                delay *= 2
            else:
                log.error(
                    "[Asyncio] Moderation failure for {} (fail-open): {}".format(
                        context_key or "unknown",
                        error,
                    )
                )
                return False

    log.warning(
        "[Asyncio] Moderation rate limit exhausted for {} (fail-open).".format(
            context_key or "unknown"
        )
    )
    return False


def clear_moderation_cache() -> None:
    _moderation_cache.cache_clear()
