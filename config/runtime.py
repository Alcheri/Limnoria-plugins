from __future__ import annotations

from typing import Any

import supybot.conf as conf


def _unwrap_value(value: Any, default: Any = None) -> Any:
    """Extract native Python values from Limnoria registry wrapper types."""
    try:
        return getattr(value, "value", value)
    except Exception:
        return default


def _to_int(value: Any, default: int) -> int:
    try:
        unwrapped = _unwrap_value(value, default)
        if unwrapped is None:
            return default
        return int(unwrapped)
    except Exception:
        return default


def _clamp_int(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def _to_bool(value: Any, default: bool = False) -> bool:
    try:
        return bool(_unwrap_value(value, default))
    except Exception:
        return default


def _to_str(value: Any, default: str = "") -> str:
    try:
        unwrapped = _unwrap_value(value, default)
        return str(unwrapped)
    except Exception:
        return default


def get_config() -> dict[str, Any]:
    default_config = {
        "max_tokens": 512,
        "cooldown": 5,
        "irc_chunk": 350,
        "api_timeout": 45,
        "botnick": "Assistant",
        "language": "British",
        "debug": False,
    }

    supybot_conf = getattr(conf, "supybot", None)
    plugins_conf = getattr(supybot_conf, "plugins", None)
    plugin_conf = getattr(plugins_conf, "Asyncio", None)
    if plugin_conf is None:
        return default_config

    return {
        "max_tokens": _clamp_int(
            _to_int(plugin_conf.maxUserTokens(), default_config["max_tokens"]),
            1,
            4096,
        ),
        "cooldown": _clamp_int(
            _to_int(plugin_conf.cooldownSeconds(), default_config["cooldown"]),
            0,
            3600,
        ),
        "irc_chunk": _clamp_int(
            _to_int(plugin_conf.ircChunkSize(), default_config["irc_chunk"]),
            80,
            450,
        ),
        "api_timeout": _clamp_int(
            _to_int(
                plugin_conf.apiTimeoutSeconds(),
                default_config["api_timeout"],
            ),
            5,
            300,
        ),
        "botnick": _to_str(plugin_conf.botnick(), default_config["botnick"]),
        "language": _to_str(
            plugin_conf.language(), default_config["language"]
        ),
        "debug": _to_bool(plugin_conf.debugMode(), default_config["debug"]),
    }
