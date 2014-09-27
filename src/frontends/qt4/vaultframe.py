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

import re
import os

from PyQt4 import QtGui
from PyQt4.QtCore import (Qt, QVariant, QTimer, QUrl, QObject, QEventLoop,
    QThread, SIGNAL, QBuffer)

from .favicon import FaviconUpdater
from .loadframe import LoadFrame
from .recordframe import RecordFrame
from .settings import (Settings, COLUMNS, COLUMNS_BY_FIELD, VAULT_EXT, ALL_EXT,
    icon_from_resources)

from ...config import config
from ...vault import Vault


class VaultFrame(QtGui.QMainWindow):
    '''
    Displays (and lets the user edit) the Vault.
    '''
    class VTWidgetRecordItem(QtGui.QTreeWidgetItem):
        '''
        QTreeWidgetItem that contains the contents of a Record.
        '''
        def __init__(self, *args, **kwargs):
            self._record = None
            super(VaultFrame.VTWidgetRecordItem,
                self).__init__(*args, **kwargs)
            self.setFlags(self.flags() | Qt.ItemIsEditable)
            self.setIcon(0, icon_from_resources('text-x-generic'))

        def type_(self):
            return 'record'

        def data(self, column, role):
            '''
            Overrides the base classes method.
            '''
            # column 10 is reserved for Record
            if column == 10:
                return self._record
            elif role in (Qt.DisplayRole, Qt.EditRole):
                field = COLUMNS[column]['field']
                value = self._record and getattr(self._record, field)
                return QVariant(value)
            else:
                return super(VaultFrame.VTWidgetRecordItem,
                    self).data(column, role)

        def setData(self, column, role, value):
            '''
            Overrides the base classes method.
            '''
            # column 10 is reserved for Record
            if column == 10:
                self._record = value
                tree = self.treeWidget()
                tree.emit(tree.urlUpdated, self)
            elif role in (Qt.DisplayRole, Qt.EditRole):
                if self._record:
                    field = COLUMNS[column]['field']
                    old_value = getattr(self._record, field)
                    value = unicode(value.toString())
                    setattr(self._record, field, value)
                    if old_value != value:
                        self.emitDataChanged()
                        if field == 'url':
                            tree = self.treeWidget()
                            tree.emit(tree.urlUpdated, self)

            else:
                return super(VaultFrame.VTWidgetRecordItem,
                    self).setData(column, role, value)

    class VTWidgetGroupItem(QtGui.QTreeWidgetItem):
        '''
        QTreeWidgetItem that contains the contents of a Group.
        '''
        def __init__(self, *args, **kwargs):
            super(VaultFrame.VTWidgetGroupItem,
                self).__init__(*args, **kwargs)
            self.setFlags(self.flags() | Qt.ItemIsEditable)
            self.setIcon(0, icon_from_resources('folder'))

        def type_(self):
            return 'group'

        def setData(self, column, role, value):
            '''
            Overrides the base classes method.
            '''
            if column == 0 and role in (
                    Qt.DisplayRole, Qt.EditRole):
                if not value.toString():
                    value = QVariant('<Group>')
                if self.data(column, role) != value:
                    # update childs
                    field = COLUMNS[column]['field']
                    for child in map(self.child, range(self.childCount())):
                        if child.type_() == 'record':
                            child.setData(COLUMNS_BY_FIELD['group'],
                                Qt.EditRole, value)
            return super(VaultFrame.VTWidgetGroupItem,
                self).setData(column, role, value)

    class VaultTreeWidget(QtGui.QTreeWidget):
        '''
        QTreeWidget that contains the contents of a Vault.
        '''
        def __init__(self, *args, **kwargs):
            self.vault = None
            self.urlUpdated = SIGNAL('urlUpdated')
            super(VaultFrame.VaultTreeWidget, self).__init__(*args, **kwargs)
            self.setHeaderLabels(map(lambda x: x['label'], COLUMNS[:2]))
            self.setColumnWidth(0, 250)
            self.setSortingEnabled(True)
            self.sortItems(0, Qt.AscendingOrder)

        def on_favicon_ready(self, item, image):
            try:
                icon = QtGui.QIcon(QtGui.QPixmap(image))
                if icon.isNull():
                    icon = icon_from_resources('text-x-generic')
                item.setIcon(0, icon)
            except:
                item.setIcon(0, icon_from_resources('text-x-generic'))

        def update_fields(self):
            self.clear()
            groups = {}
            for record in self.vault.records:
                if record.group and not record.group in groups:
                    groups[record.group] = VaultFrame.VTWidgetGroupItem(
                        self, [record.group])
                if record.group:
                    parent = groups[record.group]
                else:
                    parent = self
                item = VaultFrame.VTWidgetRecordItem(
                    parent, type=QtGui.QTreeWidgetItem.Type)
                item.setData(10, Qt.EditRole, record)

        def set_vault(self, vault):
            '''
            Set the Vault this control should display.
            '''
            self.vault = vault
            self.update_fields()
            self.select_first()

        def deselect_all(self):
            '''
            De-selects all items
            '''
            for item in self.selectedItems():
                self.setItemSelected(item, False)

        def select_first(self):
            '''
            Selects and focuses the first item (if there is one)
            '''
            self.deselect_all()
            if self.topLevelItemCount() > 0:
                self.setItemSelected(self.topLevelItem(0), True)

        def groups(self):
            return map(lambda x: x.text(0),
                filter(lambda x: x.type_() == 'group',
                map(self.topLevelItem, range(self.topLevelItemCount()))))

        def move_to_group(self, item):
            old_group = ''
            if item.parent():
                old_group = item.parent().text(0)
            new_group = item.data(COLUMNS_BY_FIELD['group'],
                Qt.EditRole).toString()
            if old_group == new_group:
                return
            self.take_child_from_parent(item)
            if new_group:
                if new_group in self.groups():
                    for i in map(self.topLevelItem, range(self.topLevelItemCount())):
                        if i.type_() == 'group' and i.text(0) == new_group:
                            group = i
                            break
                else:
                    group = VaultFrame.VTWidgetGroupItem(self, [new_group])
                group.addChild(item)
            else:
                self.addTopLevelItem(item)

        def take_child_from_parent(self, child):
            parent = child.parent()
            if parent:  # take from parent
                parent.takeChild(parent.indexOfChild(child))
            else:  # take from root
                self.takeTopLevelItem(self.indexOfTopLevelItem(child))

    def __init__(self, *args, **kwargs):
        super(VaultFrame, self).__init__(*args, **kwargs)
        self.resize(config.window_width, config.window_height)  # KILL ME

        self.list_ = VaultFrame.VaultTreeWidget()
        self.list_.itemChanged.connect(self.mark_modified)
        self.list_.itemDoubleClicked.connect(self._on_list_item_activated)

        self.updater = None
        if config.favicon:
            self.updater = FaviconUpdater()
            # signal: Updater(Thread) -> Widget(GUI)
            QObject.connect(self.updater, self.updater.faviconReady,
                self.list_.on_favicon_ready)
            # signal: Widget(GUI) -> Updater(Thread)
            QObject.connect(self.list_, self.list_.urlUpdated,
                self.updater.on_url_updated)
            self.updater.start()

        self.statusBar()

        # Set up menus
        new = QtGui.QAction(icon_from_resources('document-new'),
            '&New', self)
        new.setShortcut('Ctrl+N')
        new.triggered.connect(self._on_new)

        open_ = QtGui.QAction(icon_from_resources('document-open'),
            '&Open', self)
        open_.setShortcut('Ctrl+O')
        open_.triggered.connect(self._on_open)

        self.save = QtGui.QAction(icon_from_resources('document-save'),
            '&Save', self)
        self.save.setShortcut('Ctrl+S')
        self.save.triggered.connect(self._on_save)

        save_as = QtGui.QAction(icon_from_resources('document-save-as'),
            'Save as' + '...', self)
        save_as.setShortcut('Ctrl+Shift+S')
        save_as.triggered.connect(self._on_save_as)

        change_password = QtGui.QAction(
            'Change &Password' + '...', self)
        change_password.triggered.connect(self._on_change_password)

        open_settings = QtGui.QAction('&Settings', self)
        open_settings.triggered.connect(self._on_settings)

        exit_ = QtGui.QAction(icon_from_resources('exit'),
            'E&xit', self)
        exit_.setShortcut('Ctrl+Q')
        exit_.triggered.connect(self.close)

        add_group = QtGui.QAction(icon_from_resources('folder-new'),
            'Add &group', self)
        add_group.setShortcut('Ctrl+G')
        add_group.triggered.connect(self._on_group_add)

        add_record = QtGui.QAction(icon_from_resources('contact-new'),
            '&Add record', self)
        add_record.setShortcut('Ctrl+A')
        add_record.triggered.connect(self._on_add)

        edit_record = QtGui.QAction(icon_from_resources('document-properties'),
            '&Edit', self)
        edit_record.setShortcut('Ctrl+E')
        edit_record.triggered.connect(self._on_edit)

        remove_record = QtGui.QAction(icon_from_resources('edit-delete'),
            '&Delete', self)
        remove_record.setShortcut('Ctrl+Backspace')
        remove_record.triggered.connect(self._on_delete)

        copy_username = QtGui.QAction(icon_from_resources('edit-copy'),
            'Copy &Username', self)
        copy_username.setShortcut('Ctrl+U')
        copy_username.triggered.connect(self._on_copy_username)

        copy_password = QtGui.QAction(icon_from_resources('edit-copy'),
            'Copy &Password', self)
        copy_password.setShortcut('Ctrl+P')
        copy_password.triggered.connect(self._on_copy_password)

        open_url = QtGui.QAction(icon_from_resources('internet-web-browser'),
            'Open UR&L', self)
        open_url.setShortcut('Ctrl+L')
        open_url.triggered.connect(self._on_open_url)

        menubar = self.menuBar()

        file_ = menubar.addMenu('&File')
        file_.addAction(new)
        file_.addAction(open_)
        file_.addAction(self.save)
        file_.addAction(save_as)
        file_.addSeparator()
        file_.addAction(change_password)
        file_.addSeparator()
        file_.addAction(open_settings)
        file_.addSeparator()
        file_.addAction(exit_)

        edit = menubar.addMenu('&Edit')
        edit.addAction(add_group)
        edit.addAction(add_record)
        edit.addAction(remove_record)
        edit.addSeparator()
        edit.addAction(edit_record)
        edit.addSeparator()
        edit.addAction(copy_username)
        edit.addAction(copy_password)
        edit.addAction(open_url)

        toolbar = self.addToolBar('Toolbar')
        toolbar.addAction(new)
        toolbar.addAction(open_)
        toolbar.addAction(self.save)
        toolbar.addSeparator()
        toolbar.addAction(add_group)
        toolbar.addAction(add_record)
        toolbar.addAction(remove_record)
        toolbar.addAction(edit_record)
        toolbar.addSeparator()
        # toolbar.addAction(copy_username)
        toolbar.addAction(copy_password)
        toolbar.addAction(open_url)

        self.setWindowTitle('Loxodo - ' + 'Vault Contents')

        self.setCentralWidget(self.list_)

        self.vault_file_name = None
        self.vault_password = None
        self.vault = None
        self.mark_modified(is_modified=False)

    def mark_modified(self, item=None, i=0, is_modified=True):
        self._is_modified = is_modified
        self.save.setEnabled(is_modified)

    def open_vault(self, filename=None, password=''):
        '''
        Set the Vault that this frame should display.
        '''
        self.vault_file_name = None
        self.vault_password = None
        self.vault = Vault(password, filename=filename)
        self.list_.set_vault(self.vault)
        self.vault_file_name = filename
        self.vault_password = password
        self.mark_modified(is_modified=False)
        self.statusBar().showMessage('Read Vault contents from disk')

    def save_vault(self, filename, password):
        '''
        Write Vault contents to disk.
        '''
        try:
            self.mark_modified(is_modified=False)
            self.vault_file_name = filename
            self.vault_password = password
            self.vault.write_to_file(filename, password)
            self.statusBar().showMessage('Wrote Vault contents to disk')
        except RuntimeError:
            QtGui.QMessageBox.critical(self, 'Error writing to disk',
                'Could not write Vault contents to disk',
                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                QtGui.QMessageBox.NoButton)

    def _clear_clipboard(self, match_text=None):
        clipboard = QtGui.QApplication.clipboard()
        if match_text:
            if clipboard.text() != match_text:
                return
        clipboard.clear()
        self.statusBar().showMessage('Cleared clipboard')

    def _copy_to_clipboard(self, text, duration=None):
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(text)
        if duration:
            QTimer().singleShot(duration * 1000,
                lambda: self._clear_clipboard(text))

    def _on_list_item_activated(self, item, column):
        '''
        Event handler: Fires when user double-clicks a list entry.
        '''
        if item.type_() == 'record':
            # self.list_.editItem(item, column)
            self.list_.deselect_all()
            self.list_.setItemSelected(item, True)
            self._on_edit()
        elif item.type_() == 'group':
            self.list_.editItem(item, 0)
            # if column == 0:
            #     self.list_.editItem(item, 0)
            # else:
            #     item.setExpanded(item.isExpanded())

    def _on_settings(self):
        '''
        Event handler: Fires when user chooses this menu item.
        '''
        settings = Settings(self)
        # settings.resize(self._modal_size.width(), settings.size().height())
        settings.exec_()

    def _on_change_password(self):
        if not self.vault:
            return
        value, ok = QtGui.QInputDialog.getText(self, 'Change Vault Password',
            'New password', mode=QtGui.QLineEdit.Password)
        if not ok:
            return
        password_new = unicode(value).encode('latin1', 'replace')
        value, ok = QtGui.QInputDialog.getText(self, 'Change Vault Password',
            'Re-enter new password', mode=QtGui.QLineEdit.Password)
        if not ok:
            return
        password_new_confirm = unicode(value).encode('latin1', 'replace')
        if password_new_confirm != password_new:
            QtGui.QMessageBox.critical(self, 'Bad Password',
                'The given passwords do not match',
                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                QtGui.QMessageBox.NoButton)
            return
        self.vault_password = password_new
        self.statusBar().showMessage('Changed Vault password')
        self.mark_modified()

    def _on_new(self):
        loadframe = LoadFrame(self, is_new=True)
        loadframe.exec_()
        self._modal_size = loadframe.size()

    def _on_open(self):
        loadframe = LoadFrame(self, is_new=False)
        loadframe.exec_()
        self._modal_size = loadframe.size()

    def _on_save(self):
        if not self.vault:
            return
        if not self.vault_file_name:
            self._on_save_as()
        else:
            self.save_vault(self.vault_file_name, self.vault_password)

    def _on_save_as(self):
        if not self.vault:
            return
        home = os.path.expanduser("~")
        wildcard = ';;'.join(VAULT_EXT.keys() + ALL_EXT.keys())
        filename, filter_ = QtGui.QFileDialog.getSaveFileNameAndFilter(self,
            caption='Save new Vault as...', directory=home, filter=wildcard)
        if filename:
            filename = unicode(filename)
            filter_ = unicode(filter_)
            if filter_ in VAULT_EXT:
                ext = VAULT_EXT[filter_]
            if not filename.endswith(ext):
                filename += ext
            if filename not in config.recentvaults:
                config.recentvaults.insert(0, filename)
                config.save()
            self.save_vault(filename, self.vault_password)

    def closeEvent(self, event):
        '''
        Event handler: Fires when user chooses this menu item.
        '''
        # TODO: ask before closing
        if self.updater:
            self.updater.stop_me()
        if (config.window_width != self.size().width()
                or config.window_height != self.size().height()):
            config.window_width = self.size().width()
            config.window_height = self.size().height()
            config.save()
        super(VaultFrame, self).closeEvent(event)

    def _on_group_add(self):
        if not self.vault:
            return
        item = VaultFrame.VTWidgetGroupItem(self.list_, ['New Group'])
        self.list_.editItem(item)

    def _on_edit(self):
        '''
        Event handler: Fires when user chooses this menu item.
        '''
        item = self.list_.currentItem()
        if self.vault and item:
            if item.type_() == 'record':
                old_group = item.data(COLUMNS_BY_FIELD['group'],
                    Qt.EditRole).toString()
                recordframe = RecordFrame(self)
                recordframe.vault_record = item
                recordframe.resize(self._modal_size.width(),
                    recordframe.size().height())
                recordframe.exec_()
                new_group = item.data(COLUMNS_BY_FIELD['group'],
                    Qt.EditRole).toString()
                if old_group != new_group:
                    # self.list_.update_fields()
                    self.list_.move_to_group(item)
            elif item.type_() == 'group':
                self.list_.editItem(item)

    def _on_add(self):
        '''
        Event handler: Fires when user chooses this menu item.
        '''
        if not self.vault:
            return
        entry = self.vault.Record.create()
        item = VaultFrame.VTWidgetRecordItem(
            self.list_, type=QtGui.QTreeWidgetItem.Type)
        item.setData(10, Qt.EditRole, entry)
        recordframe = RecordFrame(self)
        recordframe.vault_record = item
        recordframe.resize(self._modal_size.width(),
            recordframe.size().height())
        if recordframe.exec_() == QtGui.QDialog.Accepted:
            self.vault.records.append(entry)
            # self.list_.update_fields()
            self.list_.move_to_group(item)
        else:
            self.list_.takeTopLevelItem(
                self.list_.indexOfTopLevelItem(item))

    def _on_delete(self):
        '''
        Event handler: Fires when user chooses this menu item.
        '''
        item = self.list_.currentItem()
        if self.vault and item:
            if item.type_() == 'record':
                entry = item.data(10, Qt.EditRole)
                if entry.user or entry.passwd:
                    reply = QtGui.QMessageBox.question(self,
                        'Really delete record?',
                        ('Are you sure you want to delete this record? '
                        'It contains a username or password and there is '
                        'no way to undo this action.'),
                        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                    if reply != QtGui.QMessageBox.Yes:
                        return
                self.vault.records.remove(entry)
            elif item.type_() == 'group':
                # move everyone in this group to root
                children = map(item.child, range(item.childCount()))
                for child in children:
                    child.setData(COLUMNS_BY_FIELD['group'],
                        Qt.EditRole, QVariant(''))
                    self.list_.take_child_from_parent(child)
                self.list_.addTopLevelItems(children)
            self.list_.take_child_from_parent(item)

    def _on_copy_username(self):
        '''
        Event handler: Fires when user chooses this menu item.
        '''
        item = self.list_.currentItem()
        if self.vault and item and item.type_() == 'record':
            title = item.data(COLUMNS_BY_FIELD['title'], Qt.EditRole).toString()
            user = item.data(COLUMNS_BY_FIELD['user'], Qt.EditRole).toString()
            self._copy_to_clipboard(user)
            self.statusBar().showMessage(
                'Copied username of "%s" to clipboard' % title)

    def _on_copy_password(self):
        '''
        Event handler: Fires when user chooses this menu item.
        '''
        item = self.list_.currentItem()
        if self.vault and item and item.type_() == 'record':
            title = item.data(COLUMNS_BY_FIELD['title'], Qt.EditRole).toString()
            passwd = item.data(COLUMNS_BY_FIELD['passwd'], Qt.EditRole).toString()
            self._copy_to_clipboard(passwd, duration=10)
            self.statusBar().showMessage(
                'Copied password of "%s" to clipboard' % title)

    def _on_open_url(self):
        '''
        Event handler: Fires when user chooses this menu item.
        '''
        item = self.list_.currentItem()
        if self.vault and item and item.type_() == 'record':
            url = unicode(item.data(COLUMNS_BY_FIELD['url'],
                Qt.EditRole).toString())
            try:
                import webbrowser
                webbrowser.open(url)
            except ImportError:
                self.statusBar().showMessage(
                    'Could not load python module '
                    '"webbrowser" needed to open "%s"' % url)
