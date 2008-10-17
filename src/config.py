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
        self.parser = SafeConfigParser()
        self.parser.read(self.get_config_filename())
        if not self.parser.has_section("base"):
            self.parser.add_section("base")

        self.recentvaults = []
        for num in range(10):
            if (not self.parser.has_option("base", "recentvaults" + str(num))):
                break
            self.recentvaults.append(self.parser.get("base", "recentvaults" + str(num)))

    def save(self):
        fname = self.get_config_filename()
        
        if (not os.path.exists(os.path.dirname(fname))):
            os.mkdir(os.path.dirname(fname))

        # remove duplicates and trim to 10 items
        _saved_recentvaults = []
        for item in self.recentvaults:
            if item in _saved_recentvaults:
                continue
            self.parser.set("base", "recentvaults" + str(len(_saved_recentvaults)), item)
            _saved_recentvaults.append(item)
            if (len(_saved_recentvaults) >= 10):
                break
        
        filehandle = open(fname, 'w')
        self.parser.write(filehandle)
        filehandle.close()

    def get_config_filename(self):
        base_fname = "loxodo"
        
        if (os.environ.has_key("XDG_CONFIG_HOME")):
            return os.path.join(os.environ["XDG_CONFIG_HOME"], base_fname + ".ini")
        if platform.system() == "Linux":
            return os.path.join(os.path.expanduser("~"), ".config", base_fname + ".ini")
        if platform.system() == "Darwin":
            return os.path.join(os.path.expanduser("~"), "Library", "Application Support", base_fname, base_fname + ".ini")
        if platform.system() == "Windows":
            return os.path.join(os.path.expanduser("~"), "Application Data", base_fname, base_fname + ".ini")

        return base_fname + ".ini"

config = Config()
