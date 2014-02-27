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

import sys
import os

sys.path.append(os.path.dirname(__file__))
from .ppygui import api as gui

from ...vault import Vault
        
class VaultFrame(gui.CeFrame):
    def __init__(self):
        gui.CeFrame.__init__(self, title="Loxodo CE", action=("Show", self._on_edit), menu="More...")

        self.cb_menu.append("Exit", callback=self._on_exit)
        self.sipp = gui.SIPPref(self)
        
        sizer = gui.VBox()

        self.list = gui.Table(self, columns=["Group", "Title", "User"])
        self.list.bind(itemactivated=self._on_item_activated)
        self.list.adjust_all()

        sizer.add(self.list, 1)
        self.sizer = sizer

        self.vault_file_name = None
        self.vault_password = None
        self._is_modified = None
        self.vault = None

    def open_vault(self, filename, password):
        """
        Set the Vault that this frame should display.
        """
        self.vault_file_name = None
        self.vault_password = None
        self._is_modified = False
        self.vault = Vault(password, filename=filename)

        self.list.redraw = False
        for record in self.vault.records:
            self.list.rows.append([record.group, record.title, record.user ])
        self.list.redraw = True
        self.list.adjust_all()

        self.vault_file_name = filename
        self.vault_password = password
    
    def _on_edit(self, ev):
        if (len(self.list.rows.selection) < 1):
            return
        index = self.list.rows.selection[0]
        record = self.vault.records[index]
        recordframe = RecordFrame()
        recordframe.set_record(record)
        recordframe.show()

    def _on_item_activated(self, ev):
        self._on_edit(ev)

    def _on_exit(self, ev):
        sys.exit()

class RecordFrame(gui.CeFrame):
    def __init__(self):
        gui.CeFrame.__init__(self, title="Loxodo CE", action=("OK", self._on_ok), menu="More...")
            
        self.cb_menu.append("Exit", callback=self._on_exit)
        self.sipp = gui.SIPPref(self)
        
        sizer = gui.VBox()

        self._table = gui.TBox(6, 2, spacing_x=2, spacing_y=2, cols_expanded=[1], rows_expanded=[5])
        lb_group = gui.Label(self, "Group: ")
        self._table.add(lb_group)
        self._tb_group = gui.Label(self, "")
        self._table.add(self._tb_group)

        lb_title = gui.Label(self, "Title: ")
        self._table.add(lb_title)
        self._tb_title = gui.Label(self, "")
        self._table.add(self._tb_title)

        lb_user = gui.Label(self, "Username: ")
        self._table.add(lb_user)
        self._tb_user = gui.Label(self, "")
        self._table.add(self._tb_user)

        lb_password = gui.Label(self, "Password: ")
        self._table.add(lb_password)
        self._tb_password = gui.Label(self, "")
        self._table.add(self._tb_password)

        lb_url = gui.Label(self, "URL: ")
        self._table.add(lb_url)
        self._tb_url = gui.Label(self, "")
        self._table.add(self._tb_url)

        lb_notes = gui.Label(self, "Notes: ")
        self._table.add(lb_notes)
        self._tb_notes = gui.Label(self, "")
        self._table.add(self._tb_notes)

        sizer.add(self._table, 1)
        self.sizer = sizer

        self._record = None

    def set_record(self, record):
        self._record = record
        self._tb_group.text = self._record.group
        self._tb_title.text = self._record.title
        self._tb_user.text = self._record.user
        self._tb_password.text = self._record.passwd
        self._tb_url.text = self._record.url
        self._tb_notes.text = self._record.notes
    
    def _on_ok(self, ev):
        self.destroy()

    def _on_exit(self, ev):
        sys.exit()

class LoadFrame(gui.CeFrame):
    def __init__(self):
        gui.CeFrame.__init__(self, title="Loxodo CE", action=("Open", self._on_open), menu="More...")
            
        self.cb_menu.append("Exit", callback=self._on_exit)
        self.sipp = gui.SIPPref(self)
        
        sizer = gui.VBox()

        table = gui.TBox(2, 2, spacing_x=2, spacing_y=2)
        lb_vault = gui.Label(self, "Vault: ")
        table.add(lb_vault)

        sizer2 = gui.HBox()
        self._tb_vault = gui.Edit(self, "")
        sizer2.add(self._tb_vault)
        bt_browse = gui.Button(self, "...", action=self._on_browse)
        sizer2.add(bt_browse)

        table.add(sizer2)

        lb_password = gui.Label(self, "Password: ")
        table.add(lb_password)
        self._tb_password = gui.Edit(self, "", password=True)
        table.add(self._tb_password)

        sizer.add(table, 1)
        self.sizer = sizer

    def _on_browse(self, ev):
        ret = gui.FileDialog.open(wildcards=[('Vault (*.psafe3)', '*.psafe3'), ('All (*.*)', '*.*')])
        self._tb_vault.text = ret
        
    def _on_open(self, ev):
        fname = self._tb_vault.text
        passwd = self._tb_password.text.encode('latin1', 'replace')
        vaultframe = VaultFrame()
        vaultframe.open_vault(fname, passwd)
        vaultframe.show()
        #APPLICATION.mainframe = vaultframe

    def _on_exit(self, ev):
        sys.exit()

APPLICATION = None
        
def main():
    APPLICATION = gui.Application(LoadFrame())
    APPLICATION.run()

main()

