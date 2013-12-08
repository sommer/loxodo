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
import wx

from .wxlocale import _
from ...vault import Vault
from ...config import config
from .recordframe import RecordFrame
from .mergeframe import MergeFrame
from .settings import Settings


class VaultFrame(wx.Frame):
    """
    Displays (and lets the user edit) the Vault.
    """
    class VaultListCtrl(wx.ListCtrl):
        """
        wx.ListCtrl that contains the contents of a Vault.
        """
        def __init__(self, *args, **kwds):
            wx.ListCtrl.__init__(self, *args, **kwds)
            self.vault = None
            self._filterstring = ""
            self.displayed_entries = []
            self.InsertColumn(0, _("Title"))
            self.InsertColumn(1, _("Username"))
            self.InsertColumn(2, _("Group"))
            self.SetColumnWidth(0, 256)
            self.SetColumnWidth(1, 128)
            self.SetColumnWidth(2, 256)
            self.sort_function = lambda e1, e2: cmp(e1.group.lower(), e2.group.lower())
            self.update_fields()

        def OnGetItemText(self, item, col):
            """
            Return display text for entries of a virtual list

            Overrides the base classes' method.
            """
            # Workaround for obscure wxPython behaviour that leads to an empty wx.ListCtrl sometimes calling OnGetItemText
            if (item < 0) or (item >= len(self.displayed_entries)):
              return "--"

            if (col == 0):
                return self.displayed_entries[item].title
            if (col == 1):
                return self.displayed_entries[item].user
            if (col == 2):
                return self.displayed_entries[item].group
            return "--"

        def update_fields(self):
            """
            Update the visual representation of list.

            Extends the base classes' method.
            """
            if not self.vault:
                self.displayed_entries = []
                return
            self.displayed_entries = [record for record in self.vault.records if self.filter_record(record)]

            self.displayed_entries.sort(self.sort_function)
            self.SetItemCount(len(self.displayed_entries))
            wx.ListCtrl.Refresh(self)

        def filter_record(self,record):
            if record.title.lower().find(self._filterstring.lower()) >= 0:
               return True

            if record.group.lower().find(self._filterstring.lower()) >= 0:
               return True

            if record.user.lower().find(self._filterstring.lower()) >= 0:
               return True

            if config.search_notes:
             if record.notes.lower().find(self._filterstring.lower()) >= 0:
                return True

            if config.search_passwd:
             if record.passwd.find(self._filterstring) >= 0:
                return True

            return False

        def set_vault(self, vault):
            """
            Set the Vault this control should display.
            """
            self.vault = vault
            self.update_fields()
            self.select_first()

        def set_filter(self, filterstring):
            """
            Sets a filter string to limit the displayed entries
            """
            self._filterstring = filterstring
            self.update_fields()
            self.select_first()

        def deselect_all(self):
            """
            De-selects all items
            """
            while (self.GetFirstSelected() != -1):
                self.Select(self.GetFirstSelected(), False)

        def select_first(self):
            """
            Selects and focuses the first item (if there is one)
            """
            self.deselect_all()
            if (self.GetItemCount() > 0):
                self.Select(0, True)
                self.Focus(0)


    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        wx.EVT_CLOSE(self, self._on_frame_close)

        self.panel = wx.Panel(self, -1)

        self._searchbox = wx.SearchCtrl(self.panel, size=(200, -1))
        self._searchbox.ShowCancelButton(True)
        self.list = self.VaultListCtrl(self.panel, -1, size=(640, 240), style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_VIRTUAL|wx.LC_EDIT_LABELS)
        self.list.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self._on_list_contextmenu)
        self.list.Bind(wx.EVT_RIGHT_UP, self._on_list_contextmenu)

        self.statusbar = self.CreateStatusBar(1, wx.ST_SIZEGRIP)

        # Set up menus
        filemenu = wx.Menu()
        temp_id = wx.NewId()
        filemenu.Append(temp_id, _("Change &Password") + "...")
        wx.EVT_MENU(self, temp_id, self._on_change_password)
        temp_id = wx.NewId()
        filemenu.Append(temp_id, _("&Merge Records from") + "...")
        wx.EVT_MENU(self, temp_id, self._on_merge_vault)
        filemenu.Append(wx.ID_ABOUT, _("&About"))
        wx.EVT_MENU(self, wx.ID_ABOUT, self._on_about)
        filemenu.Append(wx.ID_PREFERENCES, _("&Settings"))
        wx.EVT_MENU(self, wx.ID_PREFERENCES, self._on_settings)
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_EXIT, _("E&xit"))
        wx.EVT_MENU(self, wx.ID_EXIT, self._on_exit)
        self._recordmenu = wx.Menu()
        self._recordmenu.Append(wx.ID_ADD, _("&Add\tCtrl+A"))
        wx.EVT_MENU(self, wx.ID_ADD, self._on_add)
        self._recordmenu.Append(wx.ID_DELETE, _("&Delete\tCtrl+Back"))
        wx.EVT_MENU(self, wx.ID_DELETE, self._on_delete)
        self._recordmenu.AppendSeparator()
        self._recordmenu.Append(wx.ID_PROPERTIES, _("&Edit\tCtrl+E"))
        wx.EVT_MENU(self, wx.ID_PROPERTIES, self._on_edit)
        self._recordmenu.AppendSeparator()
        temp_id = wx.NewId()
        self._recordmenu.Append(temp_id, _("Copy &Username\tCtrl+U"))
        wx.EVT_MENU(self, temp_id, self._on_copy_username)
        temp_id = wx.NewId()
        self._recordmenu.Append(temp_id, _("Copy &Password\tCtrl+P"))
        wx.EVT_MENU(self, temp_id, self._on_copy_password)
        temp_id = wx.NewId()
        self._recordmenu.Append(temp_id, _("Open UR&L\tCtrl+L"))
        wx.EVT_MENU(self, temp_id, self._on_open_url)
        menu_bar = wx.MenuBar()
        menu_bar.Append(filemenu, _("&Vault"))
        menu_bar.Append(self._recordmenu, _("&Record"))
        self.SetMenuBar(menu_bar)

        self.SetTitle("Loxodo - " + _("Vault Contents"))
        self.statusbar.SetStatusWidths([-1])
        statusbar_fields = [""]
        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)

        sizer = wx.BoxSizer(wx.VERTICAL)
        _rowsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self._on_search_cancel, self._searchbox)
        self.Bind(wx.EVT_TEXT, self._on_search_do, self._searchbox)
        self._searchbox.Bind(wx.EVT_CHAR, self._on_searchbox_char)

        _rowsizer.Add(self._searchbox, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)
        sizer.Add(_rowsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        sizer.Add(self.list, 1, wx.EXPAND, 0)
        self.panel.SetSizer(sizer)
        _sz_frame = wx.BoxSizer()
        _sz_frame.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(_sz_frame)

        sizer.Fit(self)
        self.Layout()

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_item_activated, self.list)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self._on_list_item_label_edit, self.list)
        self.Bind(wx.EVT_LIST_COL_CLICK, self._on_list_column_click, self.list)

        self._searchbox.SetFocus()

        self.vault_file_name = None
        self.vault_password = None
        self.vault = None
        self._is_modified = False

    def mark_modified(self):
        self._is_modified = True
        if ((self.vault_file_name is not None) and (self.vault_password is not None)):
            self.save_vault(self.vault_file_name, self.vault_password)
        self.list.update_fields()

    def open_vault(self, filename, password):
        """
        Set the Vault that this frame should display.
        """
        self.vault_file_name = None
        self.vault_password = None
        self._is_modified = False
        self.vault = Vault(password, filename=filename)
        self.list.set_vault(self.vault)
        self.vault_file_name = filename
        self.vault_password = password
        self.statusbar.SetStatusText(_("Read Vault contents from disk"), 0)

    def save_vault(self, filename, password):
        """
        Write Vault contents to disk.
        """
        try:
            self._is_modified = False
            self.vault_file_name = filename
            self.vault_password = password
            self.vault.write_to_file(filename, password)
            self.statusbar.SetStatusText(_("Wrote Vault contents to disk"), 0)
        except RuntimeError:
            dial = wx.MessageDialog(self,
                                    _("Could not write Vault contents to disk"),
                                    _("Error writing to disk"),
                                    wx.OK | wx.ICON_ERROR
                                    )
            dial.ShowModal()
            dial.Destroy()

    def _clear_clipboard(self, match_text = None):
        if match_text:
            if not wx.TheClipboard.Open():
                raise RuntimeError(_("Could not open clipboard"))
            try:
                clip_object = wx.TextDataObject()
                if wx.TheClipboard.GetData(clip_object):
                    if clip_object.GetText() != match_text:
                        return
            finally:
                wx.TheClipboard.Close()
        wx.TheClipboard.Clear()
        self.statusbar.SetStatusText(_('Cleared clipboard'), 0)

    def _copy_to_clipboard(self, text, duration = None):
        if not wx.TheClipboard.Open():
            raise RuntimeError(_("Could not open clipboard"))
        try:
            clip_object = wx.TextDataObject(text)
            wx.TheClipboard.SetData(clip_object)
            if duration:
                wx.FutureCall(duration * 1000, self._clear_clipboard, text)
        finally:
            wx.TheClipboard.Close()

    def _on_list_item_activated(self, event):
        """
        Event handler: Fires when user double-clicks a list entry.
        """
        index = event.GetIndex()
        self.list.deselect_all()
        self.list.Select(index, True)
        self.list.Focus(index)
        self._on_copy_password(None)

    def _on_list_item_label_edit(self, event):
        """
        Event handler: Fires when user edits an entry's label.
        """
        if event.IsEditCancelled():
            return
        index = event.GetIndex()
        entry = self.list.displayed_entries[index]
        label_str = event.GetLabel()
        if entry.title == label_str:
            return
        old_title = entry.title
        entry.title = label_str
        self.list.update_fields()
        self.statusbar.SetStatusText(_('Changed title of "%s"') % old_title, 0)
        self.mark_modified()

    def _on_list_column_click(self, event):
        """
        Event handler: Fires when user clicks on the list header.
        """
        col = event.GetColumn()
        if (col == 0):
            self.list.sort_function = lambda e1, e2: cmp(e1.title.lower(), e2.title.lower())
        if (col == 1):
            self.list.sort_function = lambda e1, e2: cmp(e1.user.lower(), e2.user.lower())
        if (col == 2):
            self.list.sort_function = lambda e1, e2: cmp(e1.group.lower(), e2.group.lower())
        self.list.update_fields()

    def _on_list_contextmenu(self, dummy):
        self.PopupMenu(self._recordmenu)

    def _on_about(self, dummy):
        """
        Event handler: Fires when user chooses this menu item.
        """
        gpl_v2 = """This program is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program;
if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA."""

        developers = (
                      "Christoph Sommer",
                      "Bjorn Edstrom (Python Twofish)",
                      "Brian Gladman (C Twofish)",
                      "Tim Kuhlman",
                      "David Eckhoff",
                      "Nick Verbeck"
                      )

        about = wx.AboutDialogInfo()
        about.SetIcon(wx.Icon(os.path.join(os.path.dirname(os.path.realpath(config.get_basescript())), "resources", "loxodo-icon.png"), wx.BITMAP_TYPE_PNG, 128, 128))
        about.SetName("Loxodo")
        about.SetVersion("0.0-git")
        about.SetCopyright("Copyright (C) 2008 Christoph Sommer <mail@christoph-sommer.de>")
        about.SetWebSite("http://www.christoph-sommer.de/loxodo")
        about.SetLicense(gpl_v2)
        about.SetDevelopers(developers)
        wx.AboutBox(about)

    def _on_settings(self, dummy):
        """
        Event handler: Fires when user chooses this menu item.
        """
        settings = Settings(self)
        settings.ShowModal()
        settings.Destroy()
        self.list.update_fields()

    def _on_change_password(self, dummy):

        # FIXME: choose new SALT, B1-B4, IV values on password change? Conflicting Specs!

        dial = wx.PasswordEntryDialog(self,
                                _("New password"),
                                _("Change Vault Password")
                                )
        retval = dial.ShowModal()
        password_new = dial.Value.encode('latin1', 'replace')
        dial.Destroy()
        if retval != wx.ID_OK:
            return

        dial = wx.PasswordEntryDialog(self,
                                _("Re-enter new password"),
                                _("Change Vault Password")
                                )
        retval = dial.ShowModal()
        password_new_confirm = dial.Value.encode('latin1', 'replace')
        dial.Destroy()
        if retval != wx.ID_OK:
            return
        if password_new_confirm != password_new:
            dial = wx.MessageDialog(self,
                                    _('The given passwords do not match'),
                                    _('Bad Password'),
                                    wx.OK | wx.ICON_ERROR
                                    )
            dial.ShowModal()
            dial.Destroy()
            return

        self.vault_password = password_new
        self.statusbar.SetStatusText(_('Changed Vault password'), 0)
        self.mark_modified()

    def _on_merge_vault(self, dummy):
        wildcard = "|".join((_("Vault") + " (*.psafe3)", "*.psafe3", _("All files") + " (*.*)", "*.*"))
        dialog = wx.FileDialog(self, message = _("Open Vault..."), defaultFile = self.vault_file_name, wildcard = wildcard, style = wx.FD_OPEN)
        if dialog.ShowModal() != wx.ID_OK:
            return
        filename = dialog.GetPath()
        dialog.Destroy()

        dial = wx.PasswordEntryDialog(self,
                                _("Password"),
                                _("Open Vault...")
                                )
        retval = dial.ShowModal()
        password = dial.Value.encode('latin1', 'replace')
        dial.Destroy()
        if retval != wx.ID_OK:
            return

        merge_vault = None
        try:
            merge_vault = Vault(password, filename=filename)
        except Vault.BadPasswordError:
            dial = wx.MessageDialog(self,
                                    _('The given password does not match the Vault'),
                                    _('Bad Password'),
                                    wx.OK | wx.ICON_ERROR
                                    )
            dial.ShowModal()
            dial.Destroy()
            return
        except Vault.VaultVersionError:
            dial = wx.MessageDialog(self,
                                    _('This is not a PasswordSafe V3 Vault'),
                                    _('Bad Vault'),
                                    wx.OK | wx.ICON_ERROR
                                    )
            dial.ShowModal()
            dial.Destroy()
            return
        except Vault.VaultFormatError:
            dial = wx.MessageDialog(self,
                                    _('Vault integrity check failed'),
                                    _('Bad Vault'),
                                    wx.OK | wx.ICON_ERROR
                                    )
            dial.ShowModal()
            dial.Destroy()
            return

        oldrecord_newrecord_reason_pairs = []  # list of (oldrecord, newrecord, reason) tuples to merge
        for record in merge_vault.records:
            # check if corresponding record exists in current Vault
            my_record = None
            for record2 in self.vault.records:
                if record2.is_corresponding(record):
                    my_record = record2
                    break

            # record is new
            if not my_record:
                oldrecord_newrecord_reason_pairs.append((None, record, _("new")))
                continue

            # record is more recent
            if record.is_newer_than(my_record):
                oldrecord_newrecord_reason_pairs.append((my_record, record, _('updates "%s"') % my_record.title))
                continue

        dial = MergeFrame(self, oldrecord_newrecord_reason_pairs)
        retval = dial.ShowModal()
        oldrecord_newrecord_reason_pairs = dial.get_checked_items()
        dial.Destroy()
        if retval != wx.ID_OK:
            return

        for (oldrecord, newrecord, reason) in oldrecord_newrecord_reason_pairs:
            if oldrecord:
                oldrecord.merge(newrecord)
            else:
                self.vault.records.append(newrecord)
        self.mark_modified()

    def _on_exit(self, dummy):
        """
        Event handler: Fires when user chooses this menu item.
        """
        self.Close(True)  # Close the frame.

    def _on_edit(self, dummy):
        """
        Event handler: Fires when user chooses this menu item.
        """
        index = self.list.GetFirstSelected()
        if (index is None):
            return
        entry = self.list.displayed_entries[index]

        recordframe = RecordFrame(self)
        recordframe.vault_record = entry
        if recordframe.ShowModal() != wx.ID_CANCEL:
            self.mark_modified()
        recordframe.Destroy()

    def _on_add(self, dummy):
        """
        Event handler: Fires when user chooses this menu item.
        """
        entry = self.vault.Record.create()

        recordframe = RecordFrame(self)
        recordframe.vault_record = entry
        if recordframe.ShowModal() != wx.ID_CANCEL:
            self.vault.records.append(entry)
            self.mark_modified()
        recordframe.Destroy()

    def _on_delete(self, dummy):
        """
        Event handler: Fires when user chooses this menu item.
        """
        index = self.list.GetFirstSelected()
        if (index == -1):
            return
        entry = self.list.displayed_entries[index]

        if ((entry.user != "") or (entry.passwd != "")):
            dial = wx.MessageDialog(self,
                                    _("Are you sure you want to delete this record? It contains a username or password and there is no way to undo this action."),
                                    _("Really delete record?"),
                                    wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION
                                    )
            retval = dial.ShowModal()
            dial.Destroy()
            if retval != wx.ID_YES:
                return

        self.vault.records.remove(entry)
        self.mark_modified()

    def _on_copy_username(self, dummy):
        """
        Event handler: Fires when user chooses this menu item.
        """
        index = self.list.GetFirstSelected()
        if (index == -1):
            return
        entry = self.list.displayed_entries[index]
        try:
            self._copy_to_clipboard(entry.user)
            self.statusbar.SetStatusText(_('Copied username of "%s" to clipboard') % entry.title, 0)
        except RuntimeError:
            self.statusbar.SetStatusText(_('Error copying username of "%s" to clipboard') % entry.title, 0)

    def _on_copy_password(self, dummy):
        """
        Event handler: Fires when user chooses this menu item.
        """
        index = self.list.GetFirstSelected()
        if (index == -1):
            return
        entry = self.list.displayed_entries[index]
        try:
            self._copy_to_clipboard(entry.passwd, duration=10)
            self.statusbar.SetStatusText(_('Copied password of "%s" to clipboard') % entry.title, 0)
        except RuntimeError:
            self.statusbar.SetStatusText(_('Error copying password of "%s" to clipboard') % entry.title, 0)

    def _on_open_url(self, dummy):
        """
        Event handler: Fires when user chooses this menu item.
        """
        index = self.list.GetFirstSelected()
        if (index == -1):
            return
        entry = self.list.displayed_entries[index]
        try:
            import webbrowser
            webbrowser.open(entry.url)
        except ImportError:
            self.statusbar.SetStatusText(_('Could not load python module "webbrowser" needed to open "%s"') % entry.url, 0)

    def _on_search_do(self, dummy):
        """
        Event handler: Fires when user interacts with search field
        """
        self.list.set_filter(self._searchbox.GetValue())

    def _on_search_cancel(self, dummy):
        """
        Event handler: Fires when user interacts with search field
        """
        self._searchbox.SetValue("")

    def _on_frame_close(self, dummy):
        """
        Event handler: Fires when user closes the frame
        """
        self.Destroy()

    def _on_searchbox_char(self, evt):
        """
        Event handler: Fires when user presses a key in self._searchbox
        """
        # If "Enter" was pressed, ignore key and copy password of first match
        if evt.GetKeyCode() == wx.WXK_RETURN:
            self._on_copy_password(None)
            return

        # If "Escape" was pressed, ignore key and clear the Search box
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self._on_search_cancel(None)
            return

        # If "Up" or "Down" was pressed, ignore key and focus self.list
        if evt.GetKeyCode() in (wx.WXK_UP, wx.WXK_DOWN):
            self.list.SetFocus()
            return

        # Ignore all other keys
        evt.Skip()

