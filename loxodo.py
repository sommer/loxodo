#!/usr/bin/env python

import sys
import platform
import imp

# On Windows CE, use the "ppygui" frontend.
if platform.system() == "Windows" and platform.release() == "CE":
    from src.frontends.ppygui import loxodo
    sys.exit()

# If cmdline arguments were given, use the "cmdline" frontend.
if len(sys.argv) > 1:
    from src.frontends.cmdline import loxodo
    sys.exit()

# In all other cases, use the "wx" frontend.    
try:
    imp.find_module("wx")
    from src.frontends.wx import loxodo
    sys.exit()
except ImportError, e:
    print >> sys.stderr, 'Could not find wxPython, the wxWidgets Python bindings: %s' % e
    print >> sys.stderr, 'Falling back to cmdline frontend.'
    print >> sys.stderr, ''
    from src.frontends.cmdline import loxodo
    sys.exit()
