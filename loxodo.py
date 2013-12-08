#!/usr/bin/env python

import sys
import os
import platform

# On Windows CE, use the "ppygui" frontend.
if platform.system() == "Windows" and platform.release() == "CE":
    from src.frontends.ppygui import loxodo
    sys.exit()

# All other platforms use the Config module
from src.config import config

# store base script name, taking special care if we're "frozen" using py2app or py2exe
if hasattr(sys,"frozen") and (sys.platform != 'darwin'):
    config.set_basescript(unicode(sys.executable, sys.getfilesystemencoding()))
else:
    config.set_basescript(unicode(__file__, sys.getfilesystemencoding()))

# If cmdline arguments were given, use the "cmdline" frontend.
if len(sys.argv) > 1:
    from src.frontends.cmdline import loxodo
    sys.exit()

# In all other cases, use the "wx" frontend.    
try:
    import wx
except ImportError, e:
    print >> sys.stderr, 'Could not find wxPython, the wxWidgets Python bindings: %s' % e
    print >> sys.stderr, 'Falling back to cmdline frontend.'
    print >> sys.stderr, ''
    from src.frontends.cmdline import loxodo
    sys.exit()

from src.frontends.wx import loxodo

