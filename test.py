###
# Copyright (c) 2016, Barry Suridge
# All rights reserved.
#
#
###

import tempfile
import unittest
from pathlib import Path
import supybot.conf as conf
import supybot.ircdb as ircdb
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.world as world
from supybot.test import *
from types import SimpleNamespace
from unittest import mock
from unittest.mock import patch

try:
    from . import plugin
except ImportError:
    import plugin

if not hasattr(world, "myVerbose"):
    world.myVerbose = 0

if not hasattr(conf.supybot.networks, "test"):
    conf.registerNetwork("test")


class OnJoinTestCase(ChannelPluginTestCase):
    plugins = ("OnJoin",)
    channel = "#test"

    def _join_msg(self, nick):
        prefix = ircutils.joinHostmask(nick, "user", "example.test")
        return ircmsgs.join(self.channel, prefix=prefix)

    def _irc_proxy(self):
        return SimpleNamespace(nick=self.irc.nick, reply=mock.Mock())

    def testNoNoticeWhenDisabled(self):
        cb = self.irc.getCallback("OnJoin")
        irc_proxy = self._irc_proxy()
        with patch.object(cb, "registryValue", return_value=False):
            with patch.object(cb, "_read_random_quote", return_value="Welcome"):
                cb.doJoin(irc_proxy, self._join_msg("alice"))
        irc_proxy.reply.assert_not_called()

    def testNoticeSentWhenEnabled(self):
        cb = self.irc.getCallback("OnJoin")
        irc_proxy = self._irc_proxy()
        with patch.object(cb, "registryValue", return_value=True):
            with patch.object(cb, "_read_random_quote", return_value="Welcome"):
                cb.doJoin(irc_proxy, self._join_msg("alice"))

        irc_proxy.reply.assert_called_once_with(
            cb._teal("Welcome"),
            notice=True,
            private=True,
            to="alice",
        )

    def testNoNoticeOnBotSelfJoin(self):
        cb = self.irc.getCallback("OnJoin")
        irc_proxy = self._irc_proxy()
        self_join = self._join_msg(irc_proxy.nick)

        with patch.object(cb, "registryValue", return_value=True):
            with patch.object(
                cb, "_read_random_quote", return_value="Welcome"
            ) as read_mock:
                cb.doJoin(irc_proxy, self_join)

        read_mock.assert_not_called()
        irc_proxy.reply.assert_not_called()

    def testAddQuoteRequiresAdminCapability(self):
        self.assertError(
            "addquote test quote",
            frm="tester!foo@bar__no_testcap__baz",
        )

    def testAddQuoteSucceedsForAdminCapability(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            quotes_path = Path(tmpdir) / "quotes.txt"
            quotes_path.write_text("existing quote\n", encoding="utf-8")

            with patch.object(plugin.OnJoin, "_quotes_path", return_value=quotes_path):
                self.assertNotError("addquote new remote quote")

            self.assertEqual(
                quotes_path.read_text(encoding="utf-8").splitlines(),
                ["existing quote", "new remote quote"],
            )

    def testDelQuoteRequiresAdminCapability(self):
        self.assertError(
            "delquote 1",
            frm="tester!foo@bar__no_testcap__baz",
        )

    def testDelQuoteSucceedsForAdminCapability(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            quotes_path = Path(tmpdir) / "quotes.txt"
            quotes_path.write_text("first\nsecond\nthird\n", encoding="utf-8")

            with patch.object(plugin.OnJoin, "_quotes_path", return_value=quotes_path):
                self.assertNotError("delquote 2")

            self.assertEqual(
                quotes_path.read_text(encoding="utf-8").splitlines(),
                ["first", "third"],
            )


class OnJoinInternalTestCase(unittest.TestCase):
    def _plugin(self, quotes_path, max_quotes=3, max_recent_quotes=4):
        onjoin = plugin.OnJoin.__new__(plugin.OnJoin)
        onjoin._quotes_path = mock.Mock(return_value=quotes_path)
        onjoin.registryValue = mock.Mock(
            side_effect=lambda name, *args: {
                "maxQuotes": max_quotes,
                "maxRecentQuotes": max_recent_quotes,
            }[name]
        )
        onjoin.log = mock.Mock()
        return onjoin

    def testAppendQuoteRejectsBlankText(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            onjoin = self._plugin(Path(tmpdir) / "quotes.txt")
            self.assertIsNone(onjoin._append_quote("  \n \t "))

    def testAppendQuoteNormalisesAndPrunes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            quotes_path = Path(tmpdir) / "quotes.txt"
            quotes_path.write_text("one\ntwo\nthree\n", encoding="utf-8")
            onjoin = self._plugin(quotes_path, max_quotes=3)

            result = onjoin._append_quote("  four\nline  ")

            self.assertEqual(result, "four line")
            self.assertEqual(
                quotes_path.read_text(encoding="utf-8").splitlines(),
                ["two", "three", "four line"],
            )

    def testRecentQuotesReturnsNewestEntries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            quotes_path = Path(tmpdir) / "quotes.txt"
            quotes_path.write_text("one\ntwo\nthree\nfour\n", encoding="utf-8")
            onjoin = self._plugin(quotes_path)

            self.assertEqual(onjoin._recent_quotes(2), [(3, "three"), (4, "four")])

    def testDeleteQuoteRemovesRequestedEntry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            quotes_path = Path(tmpdir) / "quotes.txt"
            quotes_path.write_text("one\ntwo\nthree\n", encoding="utf-8")
            onjoin = self._plugin(quotes_path)

            deleted_quote = onjoin._delete_quote(2)

            self.assertEqual(deleted_quote, "two")
            self.assertEqual(
                quotes_path.read_text(encoding="utf-8").splitlines(),
                ["one", "three"],
            )

    def testDeleteQuoteRejectsMissingEntry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            quotes_path = Path(tmpdir) / "quotes.txt"
            quotes_path.write_text("one\n", encoding="utf-8")
            onjoin = self._plugin(quotes_path)

            self.assertIsNone(onjoin._delete_quote(2))

    def testReadRandomQuoteIgnoresBlankLines(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            quotes_path = Path(tmpdir) / "quotes.txt"
            quotes_path.write_text("\n\nonly quote\n\n", encoding="utf-8")
            onjoin = self._plugin(quotes_path)

            with patch.object(plugin.random, "uniform", return_value=0):
                self.assertEqual(onjoin._read_random_quote(), "only quote\n")


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
