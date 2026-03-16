###
# Copyright © 2024, Barry Suridge
# All rights reserved.
#
#
###

"""
Asyncio: Asyncio
"""

import sys
if sys.version_info < (3, 10):
    raise RuntimeError("This plugin requires Python 3.10 or newer. Please upgrade your Python installation.")

import supybot
from supybot import world

# Use this for the version of this plugin.
__version__ = "1.1"

# XXX Replace this with an appropriate author or supybot.Author instance.
__author__ = supybot.Author('Barry Suridge', 'Alcheri',
                            'barry.suridge@gmail.com')
# This is a dictionary mapping supybot.Author instances to lists of
# contributions.
__contributors__ = {}

# This is a url where the most recent plugin package can be downloaded.
__url__ = 'https://github.com/Alcheri/Asyncio'

from . import config
from . import plugin
from importlib import reload
# In case we're being reloaded.
reload(config)
reload(plugin)
# Add more reloads here if you add third-party modules and want them to be
# reloaded when this plugin is reloaded.  Don't forget to import them as well!

if world.testing:
    try:
        from . import test
    except ImportError as e:
        missing_names = {"test", f"{__name__}.test"}
        if getattr(e, "name", None) not in missing_names:
            raise

Class = plugin.Class
configure = config.configure


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
