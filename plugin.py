# -*- coding: utf-8 -*-
###
# Asyncio ChatGPT Plugin for Limnoria (Production Final)
# - Per-user + per-channel memory
# - Thread-safe asyncio execution
# - Cooldowns
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
    import aiohttp
except ImportError as ie:
    raise Exception(f"Cannot import module: {ie}")

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
def _to_int(value, default):
    try:
        return int(getattr(value, "value", value))
    except Exception:
        return default


def _to_bool(value, default=False):
    try:
        return bool(getattr(value, "value", value))
    except Exception:
        return default


def get_config():
    return {
        "max_tokens": _to_int(conf.supybot.plugins.Asyncio.get("maxUserTokens"), 512),
        "cooldown": _to_int(conf.supybot.plugins.Asyncio.get("cooldownSeconds"), 5),
        "irc_chunk": _to_int(conf.supybot.plugins.Asyncio.get("ircChunkSize"), 350),
        "botnick": conf.supybot.plugins.Asyncio.get("botnick"),
        "language": conf.supybot.plugins.Asyncio.get("language"),
        "debug": _to_bool(conf.supybot.plugins.Asyncio.get("debugMode"), False),
    }


# ----------------------------
# Global State
# ----------------------------
USER_HISTORIES = {}
USER_COOLDOWNS = {}


# ----------------------------
# Utility Functions
# ----------------------------
def count_tokens(text: str) -> int:
    return len(text.split())


def is_likely_math(query: str) -> bool:
    # Lightweight heuristic for common maths/word-problem patterns
    math_pattern = (
        r"[\d\+\-\*/\^\=<>√∑∫π()]|"
        r"\b(solve|calculate|evaluate|simplify|factor|equation|system of|"
        r"legs|heads|probability|percent|ratio|algebra|geometry|integral|derivative)\b"
    )
    return bool(re.search(math_pattern, query, re.IGNORECASE))


def clean_output(text: str) -> str:
    if not text:
        return ""

    # Remove common LaTeX wrappers
    text = text.replace("\\(", "").replace("\\)", "")
    text = text.replace("\\[", "").replace("\\]", "")
    text = text.replace("\\left", "").replace("\\right", "")
    text = text.replace("\\cdot", "⋅")

    # Keep content of \text{...}
    text = re.sub(r"\\text\{(.*?)\}", r"\1", text)

    # Remove remaining backslashes that clutter IRC
    text = text.replace("\\", "")

    # Collapse excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n", text)

    return text.strip()


def _context_key(msg) -> str:
    nick = getattr(msg, "nick", "unknown")
    channel = getattr(msg, "channel", None) or "PM"
    return f"{channel}:{nick}"


def get_user_history(context_key: str, system_prompt: str):
    if context_key not in USER_HISTORIES:
        USER_HISTORIES[context_key] = [{"role": "system", "content": system_prompt}]
    return USER_HISTORIES[context_key]


def irc_send_chunked_preserve_newlines(irc, text: str, chunk_size: int = 350):
    """
    Send text to IRC safely:
    - Preserve newlines (so '6 lines' stays 6 lines)
    - Chunk long lines to avoid truncation
    """
    text = (text or "").strip()
    if not text:
        irc.reply("AI returned no response.", prefixNick=False)
        return

    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Chunk a single long line
        while len(line) > chunk_size:
            irc.reply(line[:chunk_size], prefixNick=False)
            line = line[chunk_size:].lstrip()

        irc.reply(line, prefixNick=False)


# ----------------------------
# Moderation (Cached)
# ----------------------------
@lru_cache(maxsize=512)
def _moderation_cache(text: str) -> bool:
    try:
        response = client.moderations.create(model="omni-moderation-latest", input=text)
        return response.results[0].flagged
    except Exception as e:
        log.warning(f"[Asyncio] Moderation error (fail-open): {e}")
        return False


async def check_moderation_flag(user_input: str) -> bool:
    text = user_input.strip()
    if not text or text.startswith("!") or len(text) < 5:
        return False

    delay = 1.0
    for _attempt in range(3):
        try:
            return await asyncio.to_thread(_moderation_cache, text)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                await asyncio.sleep(delay + random.uniform(0, 0.5))
                delay *= 2
            else:
                log.error(f"[Asyncio] Moderation failure: {e}")
                break

    return False


# ----------------------------
# Chat Logic
# ----------------------------
async def chat_with_model(user_message: str, context_key: str, config: dict) -> str:
    math_mode = is_likely_math(user_message)

    if math_mode:
        system_prompt = (
            f"Your name is {config['botnick']}. "
            f"Use {config['language']} English conventions. "
            "Solve maths/word problems clearly. "
            "Return the final solution in NO MORE THAN 6 LINES. "
            "Prefer short equations and a final answer line. "
            "Do not use LaTeX; use plain text."
        )
        max_tokens = 300
        temperature = 0.2
    else:
        system_prompt = (
            f"Your name is {config['botnick']}. "
            f"Answer using {config['language']} English conventions. "
            "Be concise, friendly, and conversational."
        )
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
        log.error(f"[Asyncio] OpenAI API error for {context_key}: {e}", exc_info=True)
        return "Sorry, I ran into an API error. Please try again."


async def execute_chat_with_input_moderation(
    user_request: str, context_key: str
) -> str:
    config = get_config()

    now = time.time()
    last_time = USER_COOLDOWNS.get(context_key, 0)

    if (now - last_time) < float(config["cooldown"]):
        wait_time = int(config["cooldown"] - (now - last_time)) + 1
        return f"Please wait {wait_time}s before sending another request."

    USER_COOLDOWNS[context_key] = now

    prompt_tokens = count_tokens(user_request)
    if prompt_tokens > config["max_tokens"]:
        return (
            f"Error: Your input exceeds the max token limit of "
            f"{config['max_tokens']} (you used {prompt_tokens})."
        )

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
        irc.reply("Processing your message...", prefixNick=False)

        try:
            response = asyncio.run(
                execute_chat_with_input_moderation(user_input, context_key=context_key)
            )

            config = get_config()
            irc_send_chunked_preserve_newlines(
                irc, response, chunk_size=config["irc_chunk"]
            )

            if config["debug"]:
                log.info(f"[Asyncio DEBUG] {context_key}: {response}")

        except Exception as e:
            log.error(f"[Asyncio] Exception in chat command: {e}", exc_info=True)
            irc.reply("An unexpected error occurred. Check logs.", prefixNick=False)

    def reset(self, irc, msg, args):
        """Reset your conversation memory for this channel (or PM)."""
        context_key = _context_key(msg)

        if context_key in USER_HISTORIES:
            del USER_HISTORIES[context_key]
        if context_key in USER_COOLDOWNS:
            del USER_COOLDOWNS[context_key]

        irc.reply(
            "Your conversation memory has been reset for this context.",
            prefixNick=False,
        )

    reset = wrap(reset)


Class = Asyncio

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
