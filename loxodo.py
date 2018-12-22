#!/usr/bin/env python

import sys
import os
import platform

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
    assert(wx.__version__.startswith('4.0.'))
except AssertionError, e:
    print >> sys.stderr, 'Found incompatible wxPython, the wxWidgets Python bindings: %s' % wx.__version__
    print >> sys.stderr, 'Falling back to cmdline frontend.'
    print >> sys.stderr, ''
    from src.frontends.cmdline import loxodo
    sys.exit()
except ImportError, e:
    print >> sys.stderr, 'Could not find wxPython, the wxWidgets Python bindings: %s' % e
    print >> sys.stderr, 'Falling back to cmdline frontend.'
    print >> sys.stderr, ''
    from src.frontends.cmdline import loxodo
    sys.exit()

from src.frontends.wx import loxodo

