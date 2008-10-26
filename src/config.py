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

    def __init__(self):
        self.recentvaults = []

        self._fname = self.get_config_filename()
        self._parser = SafeConfigParser()

        if not os.path.exists(self._fname):
            self.save()

        self._parser.read(self._fname)
        if not self._parser.has_section("base"):
            self._parser.add_section("base")

        for num in range(10):
            if (not self._parser.has_option("base", "recentvaults" + str(num))):
                break
            self.recentvaults.append(self._parser.get("base", "recentvaults" + str(num)))

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

        filehandle = open(self._fname, 'w')
        self._parser.write(filehandle)
        filehandle.close()

    @staticmethod
    def get_config_filename():
        """
        Returns the full filename of the config file
        """
        base_fname = "loxodo"

        # On Mac OS X, config files go to ~/Library/Application Support/foo/
        if platform.system() == "Darwin":
            base_path = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
            if os.path.isdir(base_path):
                return os.path.join(base_path, base_fname, base_fname + ".ini")

        # On Microsoft Windows, config files go to $APPDATA/foo/
        if platform.system() in ("Windows", "Microsoft"):
            if (os.environ.has_key("APPDATA")):
                base_path = os.environ["APPDATA"]
                if os.path.isdir(base_path):
                    return os.path.join(base_path, base_fname, base_fname + ".ini")

        # Allow config directory override as per freedesktop.org XDG Base Directory Specification
        if (os.environ.has_key("XDG_CONFIG_HOME")):
            base_path = os.environ["XDG_CONFIG_HOME"]
            if os.path.isdir(base_path):
                return os.path.join(base_path, base_fname, base_fname + ".ini")

        # Default configuration path is ~/.config/foo/
        base_path = os.path.join(os.path.expanduser("~"), ".config")
        if os.path.isdir(base_path):
            return os.path.join(base_path, base_fname, base_fname + ".ini")

        # First fallback is writing to the program's base directory
        base_path = os.path.join(os.path.dirname(__file__), "..")
        if os.path.isdir(base_path):
            return os.path.join(base_path, base_fname + ".ini")

        # Final fallback is writing to the current working directory
        return base_fname + ".ini"

config = Config()
