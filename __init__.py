##
# Copyright © 2025, Barry Suridge
# All rights reserved.
#
# Credits: spline [https://github.com/andrewtryder] for the inspiration.
###

"""
Wikipedia: Wikipedia
"""

import sys

if sys.version_info < (3, 10):
    raise RuntimeError(
        "This plugin requires Python 3.10 or newer. Please upgrade your Python installation."
    )

import supybot
from supybot import world

__version__ = "1.0.0"

__author__ = supybot.Author("Barry Suridge", "Alcheri", "")

__contributors__ = {}

__url__ = "https://github.com/Alcheri/Wikipedia"

from . import config
from . import plugin
from importlib import reload

# In case we're being reloaded.
reload(config)
reload(plugin)
# Add more reloads here if you add third-party modules and want them to be
# reloaded when this plugin is reloaded.  Don't forget to import them as well!

if world.testing:
    from . import test

Class = plugin.Class
configure = config.configure


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
