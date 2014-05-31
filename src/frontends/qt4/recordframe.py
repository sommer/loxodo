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
import random
import struct

from PyQt4 import QtGui
from PyQt4.QtCore import Qt, QVariant

from .settings import COLUMNS, COLUMNS_BY_FIELD

from ...config import config


class RecordFrame(QtGui.QDialog):
    '''
    Displays (and lets the user edit) a single Vault Record.
    '''
    def __init__(self, parent):
        super(RecordFrame, self).__init__(parent)
        self.vaultframe = parent

        self.resize(200, 200)

        self._tc_title = QtGui.QLineEdit(self)
        self._tc_group = QtGui.QComboBox(self)
        self._tc_group.setEditable(True)
        self._tc_user = QtGui.QLineEdit(self)
        self._tc_passwd = QtGui.QLineEdit(self)
        self._tc_passwd.setEchoMode(QtGui.QLineEdit.Password)
        self._bt_showhide = QtGui.QPushButton('un(mask)', self)
        self._bt_showhide.clicked.connect(self._on_toggle_passwd_mask)
        self._bt_generate = QtGui.QPushButton('generate', self)
        self._bt_generate.clicked.connect(self._on_generate_passwd)
        self._tc_url = QtGui.QLineEdit(self)
        self._tc_notes = QtGui.QTextEdit(self)

        self._bt_ok = QtGui.QPushButton('OK', self)
        self._bt_ok.clicked.connect(self._on_ok)
        self._bt_cancel = QtGui.QPushButton('Cancel', self)
        self._bt_cancel.clicked.connect(self._on_cancel)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QtGui.QLabel('Title' + ':', self), 0, 0)
        grid.addWidget(self._tc_title, 0, 1, 1, 3)
        grid.addWidget(QtGui.QLabel('Group' + ':', self), 1, 0)
        grid.addWidget(self._tc_group, 1, 1, 1, 3)
        grid.addWidget(QtGui.QLabel('Username' + ':', self), 2, 0)
        grid.addWidget(self._tc_user, 2, 1, 1, 3)
        grid.addWidget(QtGui.QLabel('Password' + ':', self), 3, 0)
        grid.addWidget(self._tc_passwd, 3, 1)
        grid.addWidget(self._bt_showhide, 3, 2)
        grid.addWidget(self._bt_generate, 3, 3)
        grid.addWidget(QtGui.QLabel('URL' + ':', self), 5, 0)
        grid.addWidget(self._tc_url, 5, 1, 1, 3)
        grid.addWidget(QtGui.QLabel('Notes' + ':', self), 6, 0,
            alignment=Qt.AlignTop)
        grid.addWidget(self._tc_notes, 6, 1, 1, 3)
        grid.addWidget(self._bt_ok, 7, 2)
        grid.addWidget(self._bt_cancel, 7, 3)

        self.setWindowTitle('Loxodo - ' + 'Edit Vault Record')
        self.setLayout(grid)

        self.set_initial_focus()

        self._vault_record = None

    def update_fields(self):
        '''
        Update fields from source
        '''
        if self._vault_record:
            for column in COLUMNS:
                if column['field'] != 'group':
                    tc = getattr(self, '_tc_%s' % column['field'])
                    column = COLUMNS_BY_FIELD[column['field']]
                    tc.setText(self._vault_record.data(
                        column, Qt.EditRole).toString())

            list_ = self._vault_record.treeWidget()
            items = list(list_.groups())
            if items:
                self._tc_group.addItems([''] + items)

            group = self._vault_record.data(COLUMNS_BY_FIELD['group'],
                Qt.EditRole).toString()
            i = self._tc_group.findText(group)
            if i >= 0:
                self._tc_group.setCurrentIndex(i)
            else:
                self._tc_group.addItems([group])

    def _apply_changes(self):
        '''
        Update source from fields
        '''
        if self._vault_record:
            for column in COLUMNS:
                if column['field'] not in ['group', 'notes']:
                    tc = getattr(self, '_tc_%s' % column['field'])
                    column = COLUMNS_BY_FIELD[column['field']]
                    self._vault_record.setData(column, Qt.EditRole,
                        QVariant(tc.text()))

            self._vault_record.setData(COLUMNS_BY_FIELD['group'],
                Qt.EditRole,
                QVariant(self._tc_group.currentText()))

            self._vault_record.setData(COLUMNS_BY_FIELD['notes'],
                Qt.EditRole,
                QVariant(self._tc_notes.toPlainText()))

    def _on_cancel(self):
        '''
        Event handler: Fires when user chooses this button.
        '''
        self.reject()

    def _on_ok(self):
        '''
        Event handler: Fires when user chooses this button.
        '''
        self._apply_changes()
        self.accept()

    def _on_toggle_passwd_mask(self):
        if self._tc_passwd.echoMode() == QtGui.QLineEdit.Normal:
            self._tc_passwd.setEchoMode(QtGui.QLineEdit.Password)
        else:
            self._tc_passwd.setEchoMode(QtGui.QLineEdit.Normal)

    def _on_generate_passwd(self, dummy):
        _pwd = self.generate_password(
            alphabet=config.alphabet,
            pwd_length=config.pwlength,
            allow_reduction=config.reduction)
        self._tc_passwd.setText(_pwd)

    @staticmethod
    def _urandom(count):
        try:
            return os.urandom(count)
        except NotImplementedError:
            retval = ""
            for dummy in range(count):
                retval += struct.pack("<B", random.randint(0, 0xFF))
            return retval

    @staticmethod
    def generate_password(alphabet='abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_', pwd_length=8, allow_reduction=False):
        # remove some easy-to-mistake characters
        if allow_reduction:
            for _chr in "0OjlI1":
                alphabet = alphabet.replace(_chr, '')
        # iteratively pick one character from this alphabet to assemble password
        last_chr = 'x'
        pwd = ''
        for dummy in range(pwd_length):
            # temporarily reduce alphabet to avoid easy-to-mistake character pairs
            alphabet2 = alphabet
            if allow_reduction:
                for _chr in ('cl', 'mn', 'nm', 'nn', 'rn', 'vv', 'VV'):
                    if last_chr == _chr[0]:
                        alphabet2 = alphabet.replace(_chr[1], '')

            _chr = alphabet2[int(len(alphabet2) / 256.0 * ord(RecordFrame._urandom(1)))]
            pwd += _chr
            last_chr = _chr
        return pwd

    def set_initial_focus(self):
        self._tc_title.setFocus()
        self._tc_title.selectAll()

    def _set_vault_record(self, vault_record):
        self._vault_record = vault_record
        self.update_fields()

    def _get_vault_record(self):
        return self._vault_record

    vault_record = property(_get_vault_record, _set_vault_record)
