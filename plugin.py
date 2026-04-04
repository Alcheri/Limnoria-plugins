# -*- coding: utf-8 -*-
###
# Asyncio ChatGPT Plugin for Limnoria (Production Final)
# - Per-user + per-channel memory
# - Thread-safe asyncio execution
# - Cooldowns (encapsulated)
# - Moderation (cached)
# - Registry-safe config handling
# - Reset command
# - IRC-safe chunked output (prevents apparent truncation)
# - Math mode: answers in no more than 6 lines
###

import supybot.log as log
import supybot.conf as conf
from supybot import callbacks
from supybot.commands import wrap
import supybot.registry as registry

try:
    import asyncio
except ImportError as ie:
    raise Exception("Cannot import module: {}".format(ie))

import time
import random
import re
import os
import importlib
from functools import lru_cache

from .cooldown import CooldownManager

# ----------------------------
# Environment / API Setup
# ----------------------------


def _load_dotenv_if_available():
    try:
        dotenv = importlib.import_module("dotenv")
        load_dotenv = getattr(dotenv, "load_dotenv", None)
        if callable(load_dotenv):
            load_dotenv()
    except Exception:
        # Optional dependency; environment variables may already be set.
        pass


_load_dotenv_if_available()
client = None


def _ensure_openai_client():
    global client
    if client is not None:
        return client

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment.")

    try:
        openai_module = importlib.import_module("openai")
        openai_ctor = getattr(openai_module, "OpenAI")
    except Exception as e:
        raise ImportError(
            "The 'openai' package is required. Install it from requirements.txt."
        ) from e

    client = openai_ctor(api_key=api_key)
    return client


# ----------------------------
# Safe Limnoria Config Helpers
# ----------------------------
def _unwrap_value(value, default=None):
    """Extract native Python values from Limnoria registry wrapper types."""
    try:
        return getattr(value, "value", value)
    except Exception:
        return default


def _to_int(value, default):
    try:
        v = _unwrap_value(value, default)
        if v is None:
            return default
        return int(v)
    except Exception:
        return default


def _to_bool(value, default=False):
    try:
        return bool(_unwrap_value(value, default))
    except Exception:
        return default


def _to_str(value, default=""):
    try:
        v = _unwrap_value(value, default)
        return str(v)
    except Exception:
        return default


def get_config():
    default_config = {
        "max_tokens": 512,
        "cooldown": 5,
        "irc_chunk": 350,
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
        "max_tokens": _to_int(
            plugin_conf.maxUserTokens(), default_config["max_tokens"]
        ),
        "cooldown": _to_int(plugin_conf.cooldownSeconds(), default_config["cooldown"]),
        "irc_chunk": _to_int(plugin_conf.ircChunkSize(), default_config["irc_chunk"]),
        "botnick": _to_str(plugin_conf.botnick(), default_config["botnick"]),
        "language": _to_str(plugin_conf.language(), default_config["language"]),
        "debug": _to_bool(plugin_conf.debugMode(), default_config["debug"]),
    }


# ----------------------------
# Global State
# ----------------------------
USER_HISTORIES = {}
COOLDOWNS = CooldownManager()


# ----------------------------
# Utility Functions
# ----------------------------
def count_tokens(text):
    return len((text or "").split())


def is_likely_math(query):
    math_pattern = (
        r"[\d\+\-\*/\^\=<>√∑∫π()]|"
        r"\b(solve|calculate|evaluate|simplify|factor|equation|system of|"
        r"legs|heads|probability|percent|ratio|algebra|geometry|integral|derivative)\b"
    )
    return bool(re.search(math_pattern, query or "", re.IGNORECASE))


def clean_output(text):
    if not text:
        return ""

    text = text.replace("\\(", "").replace("\\)", "")
    text = text.replace("\\[", "").replace("\\]", "")
    text = text.replace("\\left", "").replace("\\right", "")
    text = text.replace("\\cdot", "⋅")

    text = re.sub(r"\\text\{(.*?)\}", r"\1", text)
    text = text.replace("\\", "")
    text = re.sub(r"\n\s*\n+", "\n", text)

    return text.strip()


def _context_key(msg):
    nick = getattr(msg, "nick", "unknown")
    channel = getattr(msg, "channel", None) or "PM"
    return "{}:{}".format(channel, nick)


def get_user_history(context_key, system_prompt):
    if context_key not in USER_HISTORIES:
        USER_HISTORIES[context_key] = [{"role": "system", "content": system_prompt}]
        return USER_HISTORIES[context_key]

    # If the system prompt changes (e.g., math mode vs chat mode), keep it aligned.
    # This avoids “stale” system prompts across mode changes.
    history = USER_HISTORIES[context_key]
    if (
        history
        and history[0].get("role") == "system"
        and history[0].get("content") != system_prompt
    ):
        history[0]["content"] = system_prompt
    return history


def irc_send_chunked_preserve_newlines(irc, text, chunk_size=350):
    text = (text or "").strip()
    if not text:
        irc.reply("AI returned no response.", prefixNick=False)
        return

    lines = text.splitlines()
    for line in lines:
        line = (line or "").strip()
        if not line:
            continue

        while len(line) > chunk_size:
            irc.reply(line[:chunk_size], prefixNick=False)
            line = line[chunk_size:].lstrip()

        irc.reply(line, prefixNick=False)


# ----------------------------
# Moderation (Cached)
# ----------------------------
@lru_cache(maxsize=512)
def _moderation_cache(text):
    try:
        openai_client = _ensure_openai_client()
        response = openai_client.moderations.create(
            model="omni-moderation-latest", input=text
        )
        return response.results[0].flagged
    except Exception as e:
        log.warning("[Asyncio] Moderation error (fail-open): {}".format(e))
        return False


async def check_moderation_flag(user_input):
    text = (user_input or "").strip()
    if not text or text.startswith("!") or len(text) < 5:
        return False

    delay = 1.0
    for _attempt in range(3):
        try:
            return await asyncio.to_thread(_moderation_cache, text)
        except Exception as e:
            s = str(e)
            if "429" in s or "Too Many Requests" in s:
                await asyncio.sleep(delay + random.uniform(0, 0.5))
                delay *= 2
            else:
                log.error("[Asyncio] Moderation failure: {}".format(e))
                break

    return False


# ----------------------------
# Chat Logic
# ----------------------------
async def chat_with_model(user_message, context_key, config):
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

    history = get_user_history(context_key, system_prompt)
    history.append({"role": "user", "content": user_message})

    # Trim history per context
    if len(history) > 12:
        USER_HISTORIES[context_key] = [history[0]] + history[-10:]
        history = USER_HISTORIES[context_key]

    try:
        openai_client = _ensure_openai_client()
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model="gpt-4o-mini",
            messages=history,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
        )

        reply = (response.choices[0].message.content or "").strip()
        history.append({"role": "assistant", "content": reply})
        return clean_output(reply)

    except Exception as e:
        log.error(
            "[Asyncio] OpenAI API error for {}: {}".format(context_key, e),
            exc_info=True,
        )
        return "Sorry, I ran into an API error. Please try again."


async def execute_chat_with_input_moderation(user_request, context_key, config):
    # Cooldown gate (BEFORE any token counting, moderation, or API calls)
    now = time.time()
    msg_wait = COOLDOWNS.should_wait_message(context_key, now, config["cooldown"])
    if msg_wait:
        return msg_wait

    # Record immediately (defensive: prevents burst spam if downstream hangs)
    COOLDOWNS.record(context_key, now)

    # Token limit (approx)
    prompt_tokens = count_tokens(user_request)
    if prompt_tokens > config["max_tokens"]:
        return (
            "Error: Your input exceeds the max token limit of "
            "{max_tokens} (you used {used})."
        ).format(max_tokens=config["max_tokens"], used=prompt_tokens)

    # Moderation
    flagged = await check_moderation_flag(user_request)
    if flagged:
        return "I'm sorry, but your input has been flagged as inappropriate."

    return await chat_with_model(user_request, context_key, config)


# ----------------------------
# Limnoria Plugin Class
# ----------------------------
class Asyncio(callbacks.Plugin):
    """Async ChatGPT plugin with per-channel+per-user memory and math-friendly output."""

    threaded = True

    @wrap(["text"])
    def chat(self, irc, msg, args, user_input):
        """<message> -- Chat with the AI (per-channel + per-user memory)."""

        context_key = _context_key(msg)
        config = get_config()

        # ---- Pre-cooldown check (UX polish) ----
        now = time.time()
        msg_wait = COOLDOWNS.should_wait_message(context_key, now, config["cooldown"])

        if msg_wait:
            irc.reply(msg_wait, prefixNick=False)
            return

        # Show processing only if we're actually proceeding
        try:
            _ensure_openai_client()
        except ValueError:
            irc.reply(
                "OPENAI_API_KEY is not configured. Set it in your environment or .env file.",
                prefixNick=False,
            )
            return

        irc.reply("Processing your message...", prefixNick=False)

        try:
            response = asyncio.run(
                execute_chat_with_input_moderation(
                    user_input, context_key=context_key, config=config
                )
            )

            irc_send_chunked_preserve_newlines(
                irc, response, chunk_size=config["irc_chunk"]
            )

            if config["debug"]:
                log.info("[Asyncio DEBUG] {}: {}".format(context_key, response))

        except Exception as e:
            log.error(
                "[Asyncio] Exception in chat command: {}".format(e), exc_info=True
            )
            irc.reply("An unexpected error occurred. Check logs.", prefixNick=False)

    def resetCommand(self, irc, msg, args):
        """Reset your conversation memory for this channel (or PM)."""
        context_key = _context_key(msg)

        if context_key in USER_HISTORIES:
            del USER_HISTORIES[context_key]

        # New: cooldown clear via manager
        COOLDOWNS.clear(context_key)

        irc.reply(
            "Your conversation memory has been reset for this context.",
            prefixNick=False,
        )

    reset = wrap(resetCommand)  # pyright: ignore[reportAssignmentType]


Class = Asyncio

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
