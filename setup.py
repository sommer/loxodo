#!/usr/bin/env python
"""
py2app/py2exe build script for Loxodo.

Usage (Mac OS X):
    python setup.py py2app

Usage (Windows):
    python setup.py py2exe
"""

import sys
from setuptools import setup

mainscript = 'loxodo.py'

if sys.platform == 'darwin':
	extra_options = dict(
		setup_requires = ['py2app'],
		app = [mainscript],
		options = dict(
			py2app = dict(
				argv_emulation = True,
				iconfile = 'resources/loxodo-icon.icns',
				packages = ['src', 'wx'],
				site_packages = True,
				resources = ['resources', 'locale']
			)
		),
	)
elif sys.platform == 'win32':
	extra_options = dict(
		setup_requires = ['py2exe'],
		app = [mainscript],
	)
else:
	extra_options = dict(
		scripts = [mainscript],
	)

setup(
	name="Loxodo",
	**extra_options
)

