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

if sys.platform == 'darwin':
    extra_options = dict(
        name="Loxodo",
        setup_requires = ['py2app'],
        app = ['loxodo.py'],
        options = dict(
            py2app = dict(
                argv_emulation = True,
                iconfile = 'resources/loxodo-icon.icns',
                packages = ['src', 'wx'],
                site_packages = True,
                resources = ['resources', 'locale', 'LICENSE.txt', 'README.txt']
            )
        )
    )
    setup(**extra_options)
elif sys.platform == 'win32':
    import py2exe
    import os

    # create list of needed data files
    dataFiles = []
    for subdir in ('resources', 'locale'):
        for root, dirs, files in os.walk(subdir):
            if not files:
                next
            files = []
            for filename in files:
                files.append(os.path.join(root, filename))
            if not files:
                next
            dataFiles.append((root, files))

    extra_options = dict(
        setup_requires = ['py2exe'],
        windows = ['loxodo.py'],
        data_files = dataFiles,
        options = dict(
            py2exe = dict(
                excludes = 'ppygui'
            )
        )
    )
    setup(**extra_options)
else:
    extra_options = dict(
        scripts = ['loxodo.py'],
    )
    setup(**extra_options)


