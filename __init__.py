###
# Copyright (c) 2014, spline
# Copyright © MMXXIV, Barry Suridge
# All rights reserved.
###

"""
WorldTime: look up current time and timezone info for various locations
"""

import supybot
import supybot.world as world

__version__ = "2024.12.26+git"

__author__ = supybot.Author("reticulatingspline", "spline", "")

__maintainer__ = getattr(
    supybot.authors,
    "Alcheri",
    supybot.Author("Barry Suridge", "", "barry.suridge@gmail.com"),
)

__url__ = "https://github.com/Alcheri/WorldTime"

import sys

if sys.version_info <= (3, 9):
    raise RuntimeError("This plugin requires Python 3.9 or above.")
from . import config
from . import plugin
from importlib import reload

reload(config)
reload(plugin)

if world.testing:
    from . import test

Class = plugin.Class
configure = config.configure


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
