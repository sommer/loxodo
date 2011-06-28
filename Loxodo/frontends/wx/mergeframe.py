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

import wx

from .wxlocale import _


class MergeFrame(wx.Dialog):
    """
    Displays a list of Vault Records for interactive merge of Vaults.
    """
    def __init__(self, parent, oldrecord_newrecord_reason_pairs):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

        self.panel = wx.Panel(self, -1)

        _sz_main = wx.BoxSizer(wx.VERTICAL)

        _lb_text = wx.StaticText(self.panel, -1, _("Select the Records to merge into this Vault") + ":")
        _sz_main.Add(_lb_text)

        self._cl_records = wx.CheckListBox(self.panel, -1)
        self._cl_records.AppendItems(['"' + newrecord.title + '" (' + reason + ')' for (oldrecord, newrecord, reason) in oldrecord_newrecord_reason_pairs])
        for i in range(len(oldrecord_newrecord_reason_pairs)):
            self._cl_records.Check(i)
        _sz_main.Add(self._cl_records, 1, wx.EXPAND | wx.GROW)

        _ln_line = wx.StaticLine(self.panel, -1, size=(20, -1), style=wx.LI_HORIZONTAL)
        _sz_main.Add(_ln_line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self.panel, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btn = wx.Button(self.panel, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        _sz_main.Add(btnsizer, 0, wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM, 5)

        self.panel.SetSizer(_sz_main)
        _sz_frame = wx.BoxSizer()
        _sz_frame.Add(self.panel, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(_sz_frame)

        self.SetTitle("Loxodo - " + _("Merge Vault Records"))
        self.Layout()

        self.Fit()
        self.SetMinSize(self.GetSize())

        self._vault_record = None
        self.refresh_subscriber = None

        self.oldrecord_newrecord_reason_pairs = oldrecord_newrecord_reason_pairs

    def get_checked_items(self):
        return [self.oldrecord_newrecord_reason_pairs[i] for i in range(len(self.oldrecord_newrecord_reason_pairs)) if self._cl_records.IsChecked(i)]

