###
# Copyright (c) 2020 - 2026, Barry Suridge
# All rights reserved.
#
#
###

from supybot.test import *
from unittest.mock import patch
import subprocess
class MyPingTestCase(ChannelPluginTestCase):
    plugins = ("MyPing",)
    config = {"supybot.plugins.myping.enable": True}

    @staticmethod
    def _successful_ping_output():
        return (
            "PING google.com (142.250.66.14): 56 data bytes\n"
            "64 bytes from 142.250.66.14: icmp_seq=0 ttl=57 time=23.4 ms\n"
            "\n"
            "--- google.com ping statistics ---\n"
            "1 packets transmitted, 1 received, 0% packet loss, time 0ms\n"
            "round-trip min/avg/max = 23.400/23.400/23.400 ms"
        )

    @patch("MyPing.plugin.subprocess.check_output")
    def testPingReachable(self, mock_check_output):
        mock_check_output.return_value = self._successful_ping_output()
        self.assertRegexp("myping ping google.com", "is Reachable")

    @patch("MyPing.plugin.subprocess.check_output")
    def testPingNotReachable(self, mock_check_output):
        mock_check_output.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["ping", "google.com"]
        )
        self.assertRegexp("myping ping google.com", "Not Reachable")


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
