#!/usr/bin/env python

#
# Loxodo -- Password Safe V3 compatible Password Vault
# Copyright (C) 2008-2018 Christoph Sommer <mail@christoph-sommer.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

from __future__ import print_function

import sys
import os
import platform

from src.config import config

# store base script name, taking special care if we're "frozen" using py2app or py2exe
if hasattr(sys,"frozen") and (sys.platform != 'darwin'):
    config.set_basescript(sys.executable)
else:
    config.set_basescript(__file__)

# If cmdline arguments were given, use the "cmdline" frontend.
if len(sys.argv) > 1:
    from src.frontends.cmdline import loxodo
    sys.exit()

# In all other cases, use the "wx" frontend.
try:
    import wx
    assert(wx.__version__.startswith('4.0.'))
except AssertionError as e:
    print('Found incompatible wxPython, the wxWidgets Python bindings: %s' % wx.__version__, file=sys.stderr)
    print('Falling back to cmdline frontend.', file=sys.stderr)
    print('', file=sys.stderr)
    from src.frontends.cmdline import loxodo
    sys.exit()
except ImportError as e:
    print('Could not find wxPython, the wxWidgets Python bindings: %s' % e, file=sys.stderr)
    print('Falling back to cmdline frontend.', file=sys.stderr)
    print('', file=sys.stderr)
    from src.frontends.cmdline import loxodo
    sys.exit()

from src.frontends.wx import loxodo

