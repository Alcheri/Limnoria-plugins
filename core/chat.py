# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from typing import Any

import supybot.log as log

from ..core.text import clean_output, count_tokens, is_likely_math
from ..services.moderation import check_moderation_flag
from ..services.openai_client import (
    create_chat_completion_with_fallback,
    ensure_openai_client,
)
from ..state.memory import get_user_history, trim_history


async def chat_with_model(
    user_message: str,
    context_key: str,
    config: dict[str, Any],
    *,
    get_history_fn: Callable[[str, str], list[dict[str, str]]] = get_user_history,
    trim_history_fn: Callable[[str], list[dict[str, str]]] = trim_history,
    ensure_openai_client_fn: Callable[[], Any] = ensure_openai_client,
    create_completion_fn: Callable[..., Any] = create_chat_completion_with_fallback,
) -> str:
    math_mode = is_likely_math(user_message)

    if math_mode:
        system_prompt = (
            "Your name is {botnick}. "
            "Use {language} English conventions. "
            "Solve maths/word problems clearly. "
            "Return the final solution in NO MORE THAN 6 LINES. "
            "Prefer short equations and a final answer line. "
            "Do not use LaTeX; use plain text."
        ).format(botnick=config["botnick"], language=config["language"])
        max_tokens = 300
        temperature = 0.2
    else:
        system_prompt = (
            "Your name is {botnick}. "
            "Answer using {language} English conventions. "
            "Be concise, friendly, and conversational."
        ).format(botnick=config["botnick"], language=config["language"])
        max_tokens = 250
        temperature = 0.6

    history = get_history_fn(context_key, system_prompt)
    history.append({"role": "user", "content": user_message})
    history = trim_history_fn(context_key)

    try:
        openai_client = ensure_openai_client_fn()
        response = await asyncio.to_thread(
            create_completion_fn,
            openai_client,
            messages=history,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
        )

        reply = (response.choices[0].message.content or "").strip()
        history.append({"role": "assistant", "content": reply})
        return clean_output(reply)

    except Exception as error:
        log.error(
            "[Asyncio] OpenAI API error for {}: {}".format(context_key, error),
            exc_info=True,
        )
        return "Sorry, I ran into an API error. Please try again."


async def execute_chat_with_input_moderation(
    user_request: str,
    context_key: str,
    config: dict[str, Any],
    *,
    cooldown_manager: Any,
    check_moderation_flag_fn: Callable[[str], Any] = check_moderation_flag,
    chat_with_model_fn: Callable[[str, str, dict[str, Any]], Any] = chat_with_model,
    count_tokens_fn: Callable[[str | None], int] = count_tokens,
    now_fn: Callable[[], float] = time.time,
) -> str:
    now = now_fn()
    msg_wait = cooldown_manager.should_wait_message(
        context_key, now, config["cooldown"]
    )
    if msg_wait:
        return msg_wait

    cooldown_manager.record(context_key, now)

    prompt_tokens = count_tokens_fn(user_request)
    if prompt_tokens > config["max_tokens"]:
        return (
            "Error: Your input exceeds the max token limit of "
            "{max_tokens} (you used {used})."
        ).format(max_tokens=config["max_tokens"], used=prompt_tokens)

    flagged = await check_moderation_flag_fn(user_request)
    if flagged:
        return "I'm sorry, but your input has been flagged as inappropriate."

    return await chat_with_model_fn(user_request, context_key, config)
