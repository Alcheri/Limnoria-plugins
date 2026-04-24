###
# Copyright (c) 2026, Barry Suridge
# All rights reserved.
#
#
###

import tracemalloc

import psutil
from supybot import callbacks, commands
from supybot.i18n import PluginInternationalization

_ = PluginInternationalization("Mem")


class Mem(callbacks.Plugin):
    """Provides memory usage and allocation statistics."""

    threaded = True

    def __init__(self, irc):
        super().__init__(irc)
        if not tracemalloc.is_tracing():
            tracemalloc.start()

    # Dispatcher: !mem <subcommand>
    @commands.wrap(["something"])
    def mem(self, irc, msg, args, subcommand):
        """Usage: mem <usage|top|stats>"""
        sub = subcommand.lower()

        if sub == "usage":
            self._usage(irc)
        elif sub == "top":
            self._top(irc, 5)
        elif sub == "stats":
            self._stats(irc)
        else:
            irc.reply("Unknown subcommand. Use: usage, top, stats.")

    # -------------------------
    # Internal: usage
    # -------------------------
    def _usage(self, irc):
        process = psutil.Process()
        mem = process.memory_info()

        rss = mem.rss // 1024 // 1024
        vms = mem.vms // 1024 // 1024

        irc.reply(f"RSS: {rss} MB; VMS: {vms} MB")

    # -------------------------
    # Internal: top
    # -------------------------
    def _top(self, irc, count):
        snapshot = tracemalloc.take_snapshot()
        stats = snapshot.statistics("lineno")[:count]
        if not stats:
            irc.reply("No allocation statistics available yet.")
            return

        parts = []
        for stat in stats:
            size_kb = stat.size // 1024
            tb = stat.traceback[0]
            short = "/".join(tb.filename.split("/")[-2:])
            parts.append(f"{short}:{tb.lineno} ({size_kb} KB)")

        irc.reply("; ".join(parts))

    # -------------------------
    # Internal: stats
    # -------------------------
    def _stats(self, irc):
        process = psutil.Process()
        mem = process.memory_info()

        rss = mem.rss // 1024 // 1024
        vms = mem.vms // 1024 // 1024
        shared = getattr(mem, "shared", 0) // 1024 // 1024
        data = getattr(mem, "data", 0) // 1024 // 1024

        irc.reply(f"RSS: {rss} MB; VMS: {vms} MB; Shared: {shared} MB; Data: {data} MB")


Class = Mem

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
