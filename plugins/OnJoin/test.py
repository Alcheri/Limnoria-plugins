###
# Copyright (c) 2016, Barry Suridge
# All rights reserved.
#
#
###

from supybot.test import *
from unittest import mock
from unittest.mock import patch
from types import SimpleNamespace
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils


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


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
