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

from ...config import config

def get_resourcedir():
    adjacent_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'resources')
    if (os.path.exists(adjacent_dir)):
        return adjacent_dir
    else:
        return os.path.join(os.path.dirname(os.path.realpath(config.get_basescript())), "resources")

def get_localedir():
    adjacent_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'locale')
    if (os.path.exists(adjacent_dir)):
        return adjacent_dir
    else:
        return os.path.join(os.path.dirname(os.path.realpath(config.get_basescript())), "locale")
