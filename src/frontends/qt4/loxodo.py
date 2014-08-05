#
# Loxodo -- Password Safe V3 compatible Password Vault
# Copyright (C) 2014 Okami <okami@fuzetsu.info>
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
import pkgutil
import sys

from PyQt4 import Qt
from PyQt4 import QtGui

from .vaultframe import VaultFrame

from ...config import config


def main():
    # set taskbar icon in windows
    if platform.system() == 'Windows':
        import ctypes
        APPID = 'okami.loxodo.qt.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APPID)
    app = QtGui.QApplication(sys.argv)
    qpixmap = QtGui.QPixmap()
    qpixmap.loadFromData(pkgutil.get_data('resources', 'loxodo-qt.svg'))
    app.setWindowIcon(QtGui.QIcon(qpixmap))
    mainframe = VaultFrame()
    mainframe.show()
    app.exec_()


main()
