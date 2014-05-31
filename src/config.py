#
# Loxodo -- Password Safe V3 compatible Password Vault
# Copyright (C) 2008 Christoph Sommer <mail@christoph-sommer.de>
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

import os
import platform
from ConfigParser import SafeConfigParser


class Config(object):
    """
    Manages the configuration file
    """
    FRONTENDS = (
        'wx',
        'qt4',
    )

    def __init__(self):
        """
        DEFAULT VALUES
        """
        self._basescript = None
        self.recentvaults = []
        self.pwlength = 10
        self.reduction = False
        self.search_notes = False
        self.search_passwd = False
        self.alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_"
        self.frontend = 'wx'
        self.favicon = False
        self.window_width = 800
        self.window_height = 480

        self._fname, self._cache = self.get_config_files()
        self._parser = SafeConfigParser()

        if os.path.exists(self._fname):
            self._parser.read(self._fname)

        if not self._parser.has_section("base"):
            self._parser.add_section("base")

        for num in range(10):
            if (not self._parser.has_option("base", "recentvaults" + str(num))):
                break
            self.recentvaults.append(self._parser.get("base", "recentvaults" + str(num)))

        if self._parser.has_option("base", "alphabet"):
            self.alphabet = int(self._parser.get("base", "alphabet"))

        if self._parser.has_option("base", "pwlength"):
            self.pwlength = int(self._parser.get("base", "pwlength"))

        if self._parser.has_option("base", "alphabetreduction"):
            if self._parser.get("base", "alphabetreduction") == "True":
                self.reduction = True

        if self._parser.has_option("base", "search_notes"):
            if self._parser.get("base", "search_notes") == "True":
                self.search_notes = True

        if self._parser.has_option("base", "search_passwd"):
            if self._parser.get("base", "search_passwd") == "True":
                self.search_passwd = True

        if self._parser.has_option('base', 'frontend'):
            self.frontend = self._parser.get('base', 'frontend')

        if self._parser.has_option('base', 'favicon'):
            if self._parser.get('base', 'favicon') == 'True':
                self.favicon = True

        if self._parser.has_option('base', 'window_width'):
            self.window_width = int(self._parser.get('base', 'window_width'))

        if self._parser.has_option('base', 'window_height'):
            self.window_height = int(self._parser.get('base', 'window_height'))

        if not os.path.exists(self._fname):
            self.save()

    def set_basescript(self, basescript):
        self._basescript = basescript

    def get_basescript(self):
        return self._basescript

    def save(self):
        if (not os.path.exists(os.path.dirname(self._fname))):
            os.mkdir(os.path.dirname(self._fname))

        # remove duplicates and trim to 10 items
        _saved_recentvaults = []
        for item in self.recentvaults:
            if item in _saved_recentvaults:
                continue
            self._parser.set("base", "recentvaults" + str(len(_saved_recentvaults)), item)
            _saved_recentvaults.append(item)
            if (len(_saved_recentvaults) >= 10):
                break

        self._parser.set("base", "pwlength", str(self.pwlength))
        self._parser.set("base", "alphabetreduction", str(self.reduction))
        self._parser.set("base", "search_notes", str(self.search_notes))
        self._parser.set("base", "search_passwd", str(self.search_passwd))
        self._parser.set('base', 'frontend', self.frontend)
        self._parser.set('base', 'favicon', str(self.favicon))
        self._parser.set('base', 'window_width', str(self.window_width))
        self._parser.set('base', 'window_height', str(self.window_height))
        filehandle = open(self._fname, 'w')
        self._parser.write(filehandle)
        filehandle.close()

    def get_cache_dir(self):
        if not os.path.exists(self._cache):
            os.mkdir(self._cache)
        return self._cache

    @staticmethod
    def get_config_files():
        """
        Returns the full filename of the config file
        and fill path to cache directory
        """
        base_fname = "loxodo"
        base_cache = 'cache'

        # Default configuration path is ~/.config/foo/
        base_path = os.path.join(os.path.expanduser("~"), ".config")
        if os.path.isdir(base_path):
            fname = os.path.join(base_path, base_fname, base_fname + ".ini")
        else:
            # ~/.foo/
            fname = os.path.join(os.path.expanduser("~"), "." + base_fname + ".ini")

        # ~/.cache/foo/
        base_path = os.path.join(os.path.expanduser('~'), '.cache')
        if os.path.isdir(base_path):
            cache = os.path.join(base_path, base_fname)
        else:
            # ~/.foo/cache/
            cache = os.path.join(os.path.expanduser('~'), '.' + base_fname, base_cache)

        # On Mac OS X, config files go to ~/Library/Application Support/foo/
        if platform.system() == "Darwin":
            base_path = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
            if os.path.isdir(base_path):
                fname = os.path.join(base_path, base_fname, base_fname + ".ini")
                cache = os.path.join(base_path, base_fname, base_cache)

        # On Microsoft Windows, config files go to $APPDATA/foo/
        if platform.system() in ("Windows", "Microsoft"):
            if ("APPDATA" in os.environ):
                base_path = os.environ["APPDATA"]
                if os.path.isdir(base_path):
                    fname = os.path.join(base_path, base_fname, base_fname + ".ini")
                    cache = os.path.join(base_path, base_fname, base_cache)

        # Allow config directory override as per freedesktop.org XDG Base Directory Specification
        if ("XDG_CONFIG_HOME" in os.environ):
            base_path = os.environ["XDG_CONFIG_HOME"]
            if os.path.isdir(base_path):
                fname = os.path.join(base_path, base_fname, base_fname + ".ini")
                cache = os.path.join(base_path, base_fname, base_cache)

        return fname, cache

config = Config()
