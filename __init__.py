###
# Copyright (c) 2016 - 2026, Barry Suridge
# All rights reserved.
#
#
###

"""
MyDNS: An alternative to Supybot's DNS function.
"""

import sys

if sys.version_info < (3, 10):
    raise RuntimeError(
        "This plugin requires Python 3.10 or newer. Please upgrade your Python installation."
    )

import supybot
import supybot.world as world

# Use this for the version of this plugin.  You may wish to put a CVS keyword
# in here if you're keeping the plugin in CVS or some similar system.
__version__ = "1.2.0"

# XXX Replace this with an appropriate author or supybot.Author instance.
__author__ = supybot.Author("Barry Suridge", "Alcheri", "barry.suridge@outlook.com")

# This is a dictionary mapping supybot.Author instances to lists of
# contributions.
__contributors__ = {}

# This is a url where the most recent plugin package can be downloaded.
__url__ = "https://github.com/Alcheri/MyDNS"

from . import config
from . import cooldown
from . import core
from . import plugin
from . import services
from importlib import reload

# In case we're being reloaded.
reload(config)
reload(cooldown)
reload(core)
reload(services)
reload(plugin)
# Add more reloads here if you add third-party modules and want them to be
# reloaded when this plugin is reloaded.  Don't forget to import them as well!

if world.testing:
    try:
        from . import test
    except ImportError as e:
        missing_names = {"test", f"{__name__}.test"}
        missing_test_import = "cannot import name 'test'" in str(e)
        if getattr(e, "name", None) not in missing_names and not missing_test_import:
            raise

Class = plugin.Class
configure = config.configure


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
