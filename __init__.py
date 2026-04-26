##
# Copyright (c) 2014, spline
# Copyright © 2025, Barry Suridge
# All rights reserved.
#
# Credits: spline [https://github.com/andrewtryder] for the inspiration.
###

"""
Wikipedia: Limnoria plugin to display summaries of Wikipedia articles on https://en.wikipedia.org/
"""

import sys

if sys.version_info < (3, 10):
    raise RuntimeError(
        "This plugin requires Python 3.10 or newer. Please upgrade your Python installation."
    )

import supybot
from supybot import world

__version__ = "1.0.0"

__author__ = supybot.Author("reticulatingspline", "spline", "")
__maintainer__ = getattr(
    supybot.authors,
    "Alcheri",
    supybot.Author("Barry Suridge", "Alcheri", "barry.suridge@gmail.com"),
)

__contributors__ = {
    supybot.Author("Barry Suridge", "Alcheri", "barry.suridge@gmail.com"): [
        "Maintenance"
    ],
}

__url__ = "https://github.com/Alcheri/Wikipedia"

from . import config
from . import plugin
from importlib import reload

# In case we're being reloaded.
reload(config)
reload(plugin)

if world.testing:
    from . import test

Class = plugin.Class
configure = config.configure

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
