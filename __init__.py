###
# Copyright (c) 2026, Barry Suridge
# All rights reserved.
#
#
###

"""
Mem: A memory profiler plugin for Limnoria that provides insights into the bot's memory usage and allocation patterns.
It offers commands to display current memory usage,top memory allocations, and detailed statistics to help
identify potential memory leaks or inefficiencies in the bot's operation.
"""

import supybot
from supybot import world

# Use this for the version of this plugin.
__version__ = "1.0.0"

# XXX Replace this with an appropriate author or supybot.Author instance.
__author__ = supybot.Author("Barry Suridge", "Alcheri", "barry.suridge@outlook.com")

# This is a dictionary mapping supybot.Author instances to lists of
# contributions.
__contributors__ = {}

# This is a url where the most recent plugin package can be downloaded.
__url__ = "https://github.com/Alcheri/Mem"

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
