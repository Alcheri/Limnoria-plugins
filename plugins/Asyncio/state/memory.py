from __future__ import annotations

from collections import OrderedDict
from typing import Any

MAX_HISTORY_CONTEXTS = 512
USER_HISTORIES: OrderedDict[str, list[dict[str, str]]] = OrderedDict()


def _prune_histories(max_contexts: int = MAX_HISTORY_CONTEXTS) -> None:
    while len(USER_HISTORIES) > max_contexts:
        USER_HISTORIES.popitem(last=False)


def make_context_key(msg: Any, network: str | None = None) -> str:
    nick = getattr(msg, "nick", "unknown")
    channel = getattr(msg, "channel", None) or "PM"
    if network:
        return f"{network}:{channel}:{nick}"
    return f"{channel}:{nick}"


def get_user_history(
    context_key: str, system_prompt: str
) -> list[dict[str, str]]:
    if context_key not in USER_HISTORIES:
        USER_HISTORIES[context_key] = [
            {"role": "system", "content": system_prompt}
        ]
        _prune_histories()
        return USER_HISTORIES[context_key]

    USER_HISTORIES.move_to_end(context_key)
    history = USER_HISTORIES[context_key]
    if (
        history
        and history[0].get("role") == "system"
        and history[0].get("content") != system_prompt
    ):
        history[0]["content"] = system_prompt

    return history


def trim_history(
    context_key: str, max_messages: int = 12
) -> list[dict[str, str]]:
    history = USER_HISTORIES.get(context_key, [])
    if len(history) > max_messages:
        USER_HISTORIES[context_key] = [history[0]] + history[-10:]
    return USER_HISTORIES.get(context_key, history)


def clear_context_history(context_key: str) -> None:
    USER_HISTORIES.pop(context_key, None)


def clear_history() -> None:
    USER_HISTORIES.clear()
