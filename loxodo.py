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


frontends = list(config.FRONTENDS)
# change frontends priority using config
if config.frontend in frontends and frontends.index(config.frontend) > 0:
    frontends.remove(config.frontend)
    frontends.insert(0, config.frontend)


for frontend in frontends:
    # update current frontend
    config.frontend = frontend
    if frontend == 'wx':
        try:
            import wx
            from src.frontends.wx import loxodo
            sys.exit()
        except ImportError as e:
            print('Could not find wxPython, the wxWidgets Python bindings: %s' % e)
            print('Falling to the next frontend.')
            print('')
    elif frontend == 'qt4':
        try:
            import PyQt4
            from src.frontends.qt4 import loxodo
            sys.exit()
        except ImportError as e:
            print('Could not find PyQt4, the Qt4 Python bindings: %s' % e)
            print('Falling to the next frontend.')
            print('')


from src.frontends.cmdline import loxodo
sys.exit()
