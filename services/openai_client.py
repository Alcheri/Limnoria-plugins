# -*- coding: utf-8 -*-

from __future__ import annotations

import importlib
import os
from typing import Any

import supybot.log as log

from ..state.runtime import OPENAI_RUNTIME, OpenAIRuntimeState


def _load_dotenv_if_available() -> None:
    try:
        dotenv = importlib.import_module("dotenv")
        load_dotenv = getattr(dotenv, "load_dotenv", None)
        if callable(load_dotenv):
            load_dotenv()
    except Exception:
        # Optional dependency; environment variables may already be set.
        pass


_load_dotenv_if_available()


def _chat_model_candidates() -> list[str]:
    """Ordered model fallback list for chat completions."""
    env_value = os.getenv("OPENAI_CHAT_MODELS", "")
    if env_value.strip():
        models = [model.strip() for model in env_value.split(",") if model.strip()]
        if models:
            return models

    return ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1", "gpt-4o"]


def _is_model_unavailable_error(error: Exception) -> bool:
    text = str(error).lower()
    signals = [
        "model",
        "does not exist",
        "not found",
        "invalid model",
        "deprecated",
        "decommissioned",
        "no longer available",
        "is not available",
    ]
    return "model" in text and any(signal in text for signal in signals[1:])


def create_chat_completion_with_fallback(
    openai_client: Any,
    runtime_state: OpenAIRuntimeState | None = None,
    **kwargs: Any,
) -> Any:
    state = runtime_state or OPENAI_RUNTIME
    candidates = _chat_model_candidates()

    if state.active_chat_model and state.active_chat_model in candidates:
        candidates = [state.active_chat_model] + [
            model for model in candidates if model != state.active_chat_model
        ]

    last_error: Exception | None = None
    for model_name in candidates:
        try:
            response = openai_client.chat.completions.create(
                model=model_name,
                **kwargs,
            )
            if state.active_chat_model != model_name:
                log.warning("[Asyncio] Chat model switched to '{}'".format(model_name))
            state.active_chat_model = model_name
            return response
        except Exception as error:
            last_error = error
            if _is_model_unavailable_error(error):
                log.warning(
                    "[Asyncio] Chat model '{}' unavailable, trying next fallback: {}".format(
                        model_name, error
                    )
                )
                continue
            raise

    if last_error:
        raise last_error
    raise RuntimeError("No chat model candidates configured.")


def ensure_openai_client(runtime_state: OpenAIRuntimeState | None = None) -> Any:
    state = runtime_state or OPENAI_RUNTIME
    if state.client is not None:
        return state.client

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment.")

    try:
        openai_module = importlib.import_module("openai")
        openai_ctor = getattr(openai_module, "OpenAI")
    except Exception as error:
        raise ImportError(
            "The 'openai' package is required. Install it from requirements.txt."
        ) from error

    state.client = openai_ctor(api_key=api_key)
    return state.client


def get_active_chat_model(
    runtime_state: OpenAIRuntimeState | None = None,
) -> str | None:
    state = runtime_state or OPENAI_RUNTIME
    return state.active_chat_model
