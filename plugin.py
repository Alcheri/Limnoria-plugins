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
    import asyncio  # NOTE: currently unused; OK to keep if you plan to use it.
except ImportError as ie:
    raise Exception("Cannot import module: {}".format(ie))

import time
import random
import re
import os
from functools import lru_cache

from openai import OpenAI
from dotenv import load_dotenv


# ----------------------------
# Plugin Config Registration
# ----------------------------
conf.registerPlugin("Asyncio", True)

conf.registerGlobalValue(
    conf.supybot.plugins.Asyncio,
    "maxUserTokens",
    registry.Integer(512, "Maximum number of user input tokens"),
)

conf.registerGlobalValue(
    conf.supybot.plugins.Asyncio,
    "cooldownSeconds",
    registry.Integer(5, "Seconds between user messages"),
)

conf.registerGlobalValue(
    conf.supybot.plugins.Asyncio,
    "botnick",
    registry.String("Puss", "Bot nickname"),
)

# OpenAI handles English dialects only:
# American
# British
# Australian
# Canadian
conf.registerGlobalValue(
    conf.supybot.plugins.Asyncio,
    "language",
    registry.String("British", "Language preference"),
)

conf.registerGlobalValue(
    conf.supybot.plugins.Asyncio,
    "debugMode",
    registry.Boolean(False, "Enable debug logging"),
)

conf.registerGlobalValue(
    conf.supybot.plugins.Asyncio,
    "ircChunkSize",
    registry.Integer(350, "Max characters per IRC reply chunk"),
)


# ----------------------------
# Environment / API Setup
# ----------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set in environment.")

client = OpenAI(api_key=api_key)


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
        return int(_unwrap_value(value, default))
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
    return {
        "max_tokens": _to_int(conf.supybot.plugins.Asyncio.get("maxUserTokens"), 512),
        "cooldown": _to_int(conf.supybot.plugins.Asyncio.get("cooldownSeconds"), 5),
        "irc_chunk": _to_int(conf.supybot.plugins.Asyncio.get("ircChunkSize"), 350),
        "botnick": _to_str(conf.supybot.plugins.Asyncio.get("botnick"), "Puss"),
        "language": _to_str(conf.supybot.plugins.Asyncio.get("language"), "British"),
        "debug": _to_bool(conf.supybot.plugins.Asyncio.get("debugMode"), False),
    }


# ----------------------------
# Global State
# ----------------------------
USER_HISTORIES = {}


# ----------------------------
# Cooldown Manager (Polish Target #1)
# ----------------------------
class CooldownManager(object):
    """
    Per-context cooldown tracker.

    Behaviour matches v1.1 logic:
      - last_time defaults to 0
      - if delta < cooldown -> wait_time = int(cooldown - delta) + 1
      - record timestamp when allowed (record-before-API; defensive)
    """

    def __init__(self):
        self._store = {}  # context_key -> last_time (float)

    def should_wait_message(self, context_key, now, cooldown_s):
        if not context_key:
            return None

        cd = float(cooldown_s)
        if cd <= 0.0:
            return None

        last_time = float(self._store.get(context_key, 0.0))
        delta = float(now) - last_time

        if delta < cd:
            wait_time = int(cd - delta) + 1
            return "Please wait {}s before sending another request.".format(wait_time)

        return None

    def record(self, context_key, now):
        if not context_key:
            return
        self._store[context_key] = float(now)

    def clear(self, context_key):
        if not context_key:
            return
        self._store.pop(context_key, None)


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
        response = client.moderations.create(model="omni-moderation-latest", input=text)
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
        response = await asyncio.to_thread(
            client.chat.completions.create,
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
            log.error("[Asyncio] Exception in chat command: {}".format(e), exc_info=True)
            irc.reply("An unexpected error occurred. Check logs.", prefixNick=False)

    def reset(self, irc, msg, args):
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

    reset = wrap(reset)


Class = Asyncio

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
