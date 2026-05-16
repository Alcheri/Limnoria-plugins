###
# Copyright (c) 2026, Barry Suridge
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import importlib
import sys
import unittest
from unittest import mock
from pathlib import Path

PLUGIN_PARENT = Path(__file__).resolve().parent.parent
if str(PLUGIN_PARENT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_PARENT))

dalnetid_plugin = importlib.import_module("DALnetID.plugin")


class DALnetIDTestCase(unittest.TestCase):
    """Tests for DALnet NickServ identify message handling."""

    def testNickservIdentifyQueuesExpectedMessage(self):
        """Queue the expected NickServ identify message."""
        irc = mock.Mock()
        fake_config = mock.Mock()
        fake_config.nickservPassword.return_value = "s3cr3t"

        with mock.patch.object(
            dalnetid_plugin.plugin_config,
            "DALnetID",
            new=fake_config,
        ):
            dalnetid_plugin.nickservIdentify(irc)

        expected = dalnetid_plugin.ircmsgs.privmsg(
            "NickServ@services.dal.net",
            "IDENTIFY s3cr3t",
        )
        irc.queueMsg.assert_called_once_with(expected)


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
