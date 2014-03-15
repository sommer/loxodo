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
        """
        DEFAULT VALUES
        """
        self._basescript = None
        self.recentvaults = []
        self.pwlength = 10
        self.reduction = False
        self.search_notes = False
        self.search_passwd = False
        self.use_pwgen = False
        self.alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_"

        self._fname = self.get_config_filename()
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

        if self._parser.has_option("base", "use_pwgen"):
            if self._parser.get("base", "use_pwgen") == "True":
                self.use_pwgen = True

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
        self._parser.set("base", "use_pwgen", str(self.use_pwgen))
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
            if ("APPDATA" in os.environ):
                base_path = os.environ["APPDATA"]
                if os.path.isdir(base_path):
                    return os.path.join(base_path, base_fname, base_fname + ".ini")

        # Allow config directory override as per freedesktop.org XDG Base Directory Specification
        if ("XDG_CONFIG_HOME" in os.environ):
            base_path = os.environ["XDG_CONFIG_HOME"]
            if os.path.isdir(base_path):
                return os.path.join(base_path, base_fname, base_fname + ".ini")

        # Default configuration path is ~/.config/foo/
        base_path = os.path.join(os.path.expanduser("~"), ".config")
        if os.path.isdir(base_path):
            return os.path.join(base_path, base_fname, base_fname + ".ini")
        else:
            return os.path.join(os.path.expanduser("~"),"."+ base_fname + ".ini")

config = Config()
