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
from supybot import callbacks
from supybot.commands import wrap

try:
    import asyncio
except ImportError as ie:
    raise Exception("Cannot import module: {}".format(ie))

import time

from . import __version__ as PLUGIN_VERSION
from .config.runtime import get_config
from .cooldown import CooldownManager
from .core.chat import execute_chat_with_input_moderation
from .core.text import split_irc_reply_lines
from .services.openai_client import ensure_openai_client, get_active_chat_model
from .state.memory import clear_context_history, make_context_key

# ----------------------------
# Global State
# ----------------------------
COOLDOWNS = CooldownManager()


# ----------------------------
# Limnoria Plugin Class
# ----------------------------
class Asyncio(callbacks.Plugin):
    """Async ChatGPT plugin with per-channel+per-user memory and math-friendly output."""

    threaded = True

    @wrap(["text"])
    def chat(self, irc, msg, args, user_input):
        """<message> -- Chat with the AI (per-channel + per-user memory)."""

        context_key = make_context_key(msg)
        config = get_config()

        # ---- Pre-cooldown check (UX polish) ----
        now = time.time()
        msg_wait = COOLDOWNS.should_wait_message(context_key, now, config["cooldown"])

        if msg_wait:
            irc.reply(msg_wait, prefixNick=False)
            return

        # Show processing only if we're actually proceeding
        try:
            ensure_openai_client()
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
                    user_input,
                    context_key=context_key,
                    config=config,
                    cooldown_manager=COOLDOWNS,
                )
            )

            chunks = split_irc_reply_lines(response, chunk_size=config["irc_chunk"])
            if not chunks:
                irc.reply("AI returned no response.", prefixNick=False)
            else:
                for chunk in chunks:
                    irc.reply(chunk, prefixNick=False)

            if config["debug"]:
                log.info("[Asyncio DEBUG] {}: {}".format(context_key, response))

        except Exception as error:
            log.error(
                "[Asyncio] Exception in chat command: {}".format(error), exc_info=True
            )
            irc.reply("An unexpected error occurred. Check logs.", prefixNick=False)

    def resetCommand(self, irc, msg, args):
        """Reset your conversation memory for this channel (or PM)."""
        context_key = make_context_key(msg)

        clear_context_history(context_key)
        COOLDOWNS.clear(context_key)

        irc.reply(
            "Your conversation memory has been reset for this context.",
            prefixNick=False,
        )

    reset = wrap(resetCommand)  # pyright: ignore[reportAssignmentType]

    def chatversion(self, irc, msg, args) -> None:
        """takes no arguments

        Show the currently loaded Asyncio plugin version.
        """
        _ = (msg, args)
        active_model = get_active_chat_model()
        model_label = active_model if active_model else "not selected yet"
        irc.reply(
            f"Asyncio version: {PLUGIN_VERSION} | model: {model_label}",
            prefixNick=False,
        )

    chatversion = wrap(chatversion)  # pyright: ignore[reportAssignmentType]


Class = Asyncio

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
