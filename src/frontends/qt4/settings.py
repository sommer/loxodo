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

from ...config import config

COLUMNS = ({
    'label': 'Title',
    'field': 'title',
}, {
    'label': 'Username',
    'field': 'user',
}, {
    'label': 'Group',
    'field': 'group',
}, {
    'label': 'Password',
    'field': 'passwd',
}, {
    'label': 'URL',
    'field': 'url',
}, {
    'label': 'Notes',
    'field': 'notes',
})

COLUMNS_BY_FIELD = dict(map(
    lambda (i, column): (column['field'], i), enumerate(COLUMNS)))

VAULT_EXT = {
    'Vault (*.psafe3)': '.psafe3',
}
ALL_EXT = {
    'All files (*.*)': '.*',
}


def icon_from_resources(name):
    try:
        qpixmap = QtGui.QPixmap()
        qpixmap.loadFromData(pkgutil.get_data(
            'resources.icons', name + '.svg'))
    except IOError:
        return QtGui.QIcon.fromTheme(name)
    else:
        return QtGui.QIcon.fromTheme(name, QtGui.QIcon(qpixmap))


class Settings(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent)

        self._frontend = QtGui.QComboBox(self)
        self._frontend.addItems(config.frontends)

        # self._search_notes = QtGui.QCheckBox('Search inside notes', self)
        # self._search_passwd = QtGui.QCheckBox(
        #     'Search inside passwords', self)

        self._sc_length = QtGui.QSpinBox(self)
        self._sc_length.setRange(4, 128)

        self._cb_reduction = QtGui.QCheckBox(
            'Avoid easy to mistake chars', self)

        self._tc_alphabet = QtGui.QLineEdit(config.alphabet, self)

        self._favicon = QtGui.QCheckBox(
            'Download website icons for the records', self)

        self._bt_ok = QtGui.QPushButton('OK', self)
        self._bt_ok.clicked.connect(self._on_ok)
        self._bt_cancel = QtGui.QPushButton('Cancel', self)
        self._bt_cancel.clicked.connect(self._on_cancel)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QtGui.QLabel('Frontend', self), 0, 0)
        grid.addWidget(self._frontend, 0, 1, 1, 3)
        # grid.addWidget(self._search_notes, 1, 0, 1, 4)
        # grid.addWidget(self._search_passwd, 2, 0, 1, 4)
        grid.addWidget(QtGui.QLabel(
            'Generated Password Length', self), 3, 0)
        grid.addWidget(self._sc_length, 3, 1, 1, 3)
        grid.addWidget(QtGui.QLabel('Alphabet', self), 4, 0)
        grid.addWidget(self._tc_alphabet, 4, 1, 1, 3)
        grid.addWidget(self._cb_reduction, 5, 0, 1, 4)
        grid.addWidget(self._favicon, 6, 0, 1, 4)

        grid.addWidget(self._bt_ok, 7, 2)
        grid.addWidget(self._bt_cancel, 7, 3)

        self.setWindowTitle('Loxodo - ' + 'Settings')
        self.setLayout(grid)

        self.set_initial_focus()
        self.update_fields()

    def update_fields(self):
        '''
        Update fields from source
        '''
        i = self._frontend.findText(config.frontend)
        if i >= 0:
            self._frontend.setCurrentIndex(i)
        else:
            self._frontend.addItems([config.frontend])
        self._sc_length.setValue(config.pwlength)
        self._tc_alphabet.setText(config.alphabet)
        self._cb_reduction.setChecked(config.reduction)
        # self._search_notes.setChecked(config.search_notes)
        # self._search_passwd.setChecked(config.search_passwd)
        self._favicon.setChecked(config.favicon)

    def _apply_changes(self):
        '''
        Update source from fields
        '''
        config.frontend = str(self._frontend.currentText())
        config.pwlength = self._sc_length.value()
        config.reduction = self._cb_reduction.isChecked()
        # config.search_notes = self._search_notes.isChecked()
        # config.search_passwd = self._search_passwd.isChecked()
        config.alphabet = unicode(self._tc_alphabet.text())
        config.favicon = self._favicon.isChecked()
        config.save()

    def _on_cancel(self, dummy):
        '''
        Event handler: Fires when user chooses this button.
        '''
        self.reject()

    def _on_ok(self, evt):
        '''
        Event handler: Fires when user chooses this button.
        '''
        self._apply_changes()
        self.accept()

    def set_initial_focus(self):
        self._sc_length.setFocus()
