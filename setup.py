#!/usr/bin/env python
"""
py2app/py2exe build script for Loxodo.

Usage (Mac OS X):
    python setup.py py2app

Usage (Windows):
    python setup.py py2exe
"""
import operator
import os
import sys
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_data_files(data_dirs):
    data_files = []
    for dest, src in data_dirs:
        for subdir in map(operator.itemgetter(0), os.walk(src)):  # find all subdirs dirs
            data_files += map(lambda x: (os.path.relpath(subdir, dest), (x,)),  # py2exe config formatting
                filter(os.path.isfile,  # files only
                map(lambda x: os.path.join(subdir, x), os.listdir(subdir))))  # every file
    return data_files

METADATA = {
    'name': 'loxodo',
    'version': '1.0',
    'author': 'Christoph Sommer',
    'author_email': 'mail@christoph-sommer.de',
    'description': '''Password Safe V3 compatible Password Vault.''',
    'license': 'GPLv2+',
    'keywords': 'loxodo password safe',
    'url': 'http://www.christoph-sommer.de/loxodo',
    'long_description': read('README.txt'),
    'classifiers': [
        'Development Status :: 6 - Mature',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Security :: Cryptography',
    ],
    'packages': find_packages(),
    'scripts': ['loxodo.py', '__main__.py'],
    'data_files': get_data_files((
        ('.', 'resources'),
        ('.', 'locale'),
    )),
    # 'install_requires': ['PyQt4>=4.10.4'],
    'include_package_data': True,
}

if sys.platform == 'darwin':
    METADATA.update({
        'name': 'Loxodo',
        'setup_requires': ['py2app'],
        'app': ['loxodo.py'],
        'options': {
            'py2app': {
                'argv_emulation': True,
                'iconfile': 'resources/loxodo-icon.icns',
                'packages': ['src', 'wx'],
                'site_packages': True,
                'resources': [
                    'resources', 'locale', 'LICENSE.txt', 'README.txt'
                ],
            }
        }
    })
elif sys.platform in ('win32', 'cygwin'):
    import py2exe
    import PyQt4

    pyqt4_dir = os.path.dirname(PyQt4.__file__)
    data_dirs = (
        (os.path.join(pyqt4_dir, 'plugins'), os.path.join(pyqt4_dir, 'plugins', 'imageformats')),
    )
    data_files = get_data_files(data_dirs)
    METADATA.update({
        'setup_requires': ['py2exe'],
        'windows': [{
            'script':'loxodo.py',
            'icon_resources': [(1, 'resources/loxodo-qt.ico')],
        }],
        'data_files': METADATA['data_files'] + data_files,
        'zipfile': None,
        'options': {
            'py2exe': {
                'bundle_files': 3,
                'compressed': True,
                'includes':  [
                    'sip',
                    'PyQt4.QtSvg',
                    'PyQt4.QtXml',
                ],
                'excludes': 'ppygui',
                'dll_excludes': [
                    'w9xpopen.exe',
                    'MSVCP90.dll',
                ],
            }
        }
    })

if __name__ == '__main__':
    setup(**METADATA)
