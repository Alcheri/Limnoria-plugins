###
# Copyright (c) 2021, Barry KW Suridge
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

import unittest

import supybot.test as supybot_test

supybot_test.PluginTestCase.__test__ = False

try:
    from . import plugin as iso_plugin
except ImportError:  # pragma: no cover - allows direct unittest execution.
    import plugin as iso_plugin


class ISOTestCase(supybot_test.PluginTestCase):
    __test__ = False
    plugins = ("ISO",)


class ISOUnitTestCase(unittest.TestCase):
    def test_lookup_country_accepts_alpha2_code(self):
        self.assertEqual(iso_plugin.lookup_country("tr"), ("TR", "Türkiye"))

    def test_lookup_country_accepts_country_name(self):
        self.assertEqual(
            iso_plugin.lookup_country("myanmar"), ("MM", "Myanmar")
        )

    def test_normalise_lookup_rejects_empty_input(self):
        with self.assertRaisesRegex(
            ValueError, "Country code or name is required."
        ):
            iso_plugin.normalise_lookup(" \n\t ")

    def test_normalise_lookup_rejects_overlong_input(self):
        with self.assertRaisesRegex(
            ValueError, "Country code or name is too long."
        ):
            iso_plugin.normalise_lookup(
                "x" * (iso_plugin.MAX_LOOKUP_LENGTH + 1)
            )

    def test_lookup_country_uses_generic_unknown_error(self):
        with self.assertRaisesRegex(
            ValueError, "Unknown country code or name."
        ) as context:
            iso_plugin.lookup_country("zz\nvery noisy input")

        self.assertNotIn("zz", str(context.exception))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
