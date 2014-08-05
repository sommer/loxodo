#!/usr/bin/env python

import sys
import platform


# On Windows CE, use the "ppygui" frontend.
if platform.system() == "Windows" and platform.release() == "CE":
    from src.frontends.ppygui import loxodo
    sys.exit()

# All other platforms use the Config module
from src.config import config

# store base script name, taking special care if we're "frozen" using py2app or py2exe
if hasattr(sys, "frozen") and (sys.platform != 'darwin'):
    config.set_basescript(unicode(sys.executable, sys.getfilesystemencoding()))
else:
    config.set_basescript(unicode(__file__, sys.getfilesystemencoding()))

if set(sys.argv) & {'-i', '-h'}:
    from src.frontends.cmdline import loxodo
    sys.exit()

frontend = config.frontend
# invalid frontend, select first one
if not frontend in config.frontends:
    config.frontend = config.frontends[0]

if frontend == 'wx':
    from src.frontends.wx import loxodo
    sys.exit()
elif frontend == 'qt4':
    from src.frontends.qt4 import loxodo
    sys.exit()

# fallback frontend
from src.frontends.cmdline import loxodo
sys.exit()
