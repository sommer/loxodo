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
import pkgutil

from PyQt4 import QtGui
from PyQt4.QtCore import Qt

from .settings import VAULT_EXT, ALL_EXT

from ...config import config
from ...vault import Vault


class LoadFrame(QtGui.QDialog):
    '''
    Displays the "welcome" dialog which lets the user open a Vault.
    '''
    def __init__(self, parent=None, is_new=True):
        super(LoadFrame, self).__init__(parent)

        logo = QtGui.QLabel(self)
        qpixmap = QtGui.QPixmap()
        qpixmap.loadFromData(pkgutil.get_data('resources', 'qt-bw.svg'))
        logo.setPixmap(qpixmap)
        logo.setScaledContents(True)

        self._tc_passwd = QtGui.QLineEdit(self)
        self._tc_passwd.setEchoMode(QtGui.QLineEdit.Password)

        if is_new:
            self._tc_passwd2 = QtGui.QLineEdit(self)
            self._tc_passwd2.setEchoMode(QtGui.QLineEdit.Password)
            create = QtGui.QPushButton('Create', self)
            create.clicked.connect(self._on_new)
        else:
            self._fb_filename = QtGui.QComboBox(self)
            self._fb_filename.setEditable(True)
            if config.recentvaults:
                self._fb_filename.addItems(config.recentvaults)
            open_ = QtGui.QPushButton('Open', self)
            open_.clicked.connect(self._on_open)
            browse = QtGui.QPushButton('Browse', self)
            browse.clicked.connect(self._on_pickvault)

        cancel = QtGui.QPushButton('Cancel', self)
        cancel.clicked.connect(self.close)

        grid = QtGui.QGridLayout()
        grid.setColumnStretch(1, 1)
        grid.setSpacing(10)

        grid.addWidget(logo, 0, 0, 1, 4,
            alignment=Qt.AlignHCenter | Qt.AlignBottom)

        if is_new:
            grid.addWidget(QtGui.QLabel('Password' + ':', self), 1, 0)
            grid.addWidget(self._tc_passwd, 1, 1, 1, 3)
            grid.addWidget(QtGui.QLabel('Retype password' + ':', self), 2, 0)
            grid.addWidget(self._tc_passwd2, 2, 1, 1, 3)
            grid.addWidget(create, 3, 2)
            grid.addWidget(cancel, 3, 3)
        else:
            grid.addWidget(QtGui.QLabel('Vault' + ':', self), 1, 0)
            grid.addWidget(self._fb_filename, 1, 1, 1, 2)
            grid.addWidget(browse, 1, 3)
            grid.addWidget(QtGui.QLabel('Password' + ':', self), 2, 0)
            grid.addWidget(self._tc_passwd, 2, 1, 1, 3)
            grid.addWidget(open_, 3, 2)
            grid.addWidget(cancel, 3, 3)

        if is_new:
            self.setWindowTitle('Loxodo - ' + 'Create Vault')
        else:
            self.setWindowTitle('Loxodo - ' + 'Open Vault')

        self.setLayout(grid)

        # self.updateGeometry()
        # size = self.size()
        # self.resize(size)
        # size.setWidth(size.width() * 2)
        # print(self.size())

        self._tc_passwd.setFocus()

    def _on_pickvault(self):
        home = os.path.expanduser("~")
        wildcard = ";;".join(VAULT_EXT.keys() + ALL_EXT.keys())
        filename, filter_ = QtGui.QFileDialog.getOpenFileNameAndFilter(self,
            caption='Open file', directory=home, filter=wildcard)
        if filename:
            i = self._fb_filename.findText(filename)
            if i >= 0:
                self._fb_filename.setCurrentIndex(i)
            else:
                self._fb_filename.addItems([filename])
            self._tc_passwd.setFocus()

    def _on_new(self):
        password = unicode(self._tc_passwd.text()).encode(
            'latin1', 'replace')
        password2 = unicode(self._tc_passwd2.text()).encode(
            'latin1', 'replace')
        if password != password2:
            QtGui.QMessageBox.warning(self, 'Bad Password',
                'The given passwords does not match',
                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                QtGui.QMessageBox.NoButton)
            self._tc_passwd.setFocus()
            self._tc_passwd.selectAll()
        else:
            self.parentWidget().open_vault(password=password)
            self.close()

    def _on_open(self):
        try:
            password = unicode(self._tc_passwd.text()).encode(
                'latin1', 'replace')
            filename = unicode(self._fb_filename.currentText())
            self.parentWidget().open_vault(
                filename=filename, password=password)
            if (filename in config.recentvaults
                    and config.recentvaults.index(filename) != 0):
                config.recentvaults.remove(filename)
            if filename not in config.recentvaults:
                config.recentvaults.insert(0, filename)
                config.save()
            self.close()
        except Vault.BadPasswordError:
            QtGui.QMessageBox.warning(self, 'Bad Password',
                'The given password does not match the Vault',
                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                QtGui.QMessageBox.NoButton)
            self._tc_passwd.setFocus()
            self._tc_passwd.selectAll()
        except Vault.VaultVersionError:
            QtGui.QMessageBox.warning(self, 'Bad Vault',
                'This is not a PasswordSafe V3 Vault',
                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                QtGui.QMessageBox.NoButton)
        except (Vault.VaultFormatError, IOError):
            QtGui.QMessageBox.warning(self, 'Bad Vault',
                'Vault integrity check failed',
                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                QtGui.QMessageBox.NoButton)
