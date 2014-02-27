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
import random
import struct
import wx

from .wxlocale import _
from ...config import config


class Settings(wx.Dialog):
    """
    Displays (and lets the user edit) a single Vault Record.
    """
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent)
        wx.EVT_CLOSE(self, self._on_frame_close)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_escape)

        self.panel = wx.Panel(self, -1)

        _sz_main = wx.BoxSizer(wx.VERTICAL)
        _sz_fields = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        _sz_fields.AddGrowableCol(1)
        _sz_fields.AddGrowableRow(5)

        self._search_notes = self._add_a_checkbox(_sz_fields,_("Search inside notes") + ":")
        self._search_passwd = self._add_a_checkbox(_sz_fields,_("Search inside passwords") + ":")

        self._sc_length = self._add_a_spincontrol(_sz_fields, _("Generated Password Length") + ":",4,128)

        _sz_main.Add(_sz_fields, 1, wx.EXPAND | wx.GROW)

        self._cb_reduction = self._add_a_checkbox(_sz_fields,_("Avoid easy to mistake chars") + ":")

        self._tc_alphabet = self._add_a_textcontrol(_sz_fields,_("Alphabet")+ ":",config.alphabet)

        _ln_line = wx.StaticLine(self.panel, -1, size=(20, -1), style=wx.LI_HORIZONTAL)
        _sz_main.Add(_ln_line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self.panel, wx.ID_CANCEL)
        wx.EVT_BUTTON(self, wx.ID_CANCEL, self._on_cancel)
        btnsizer.AddButton(btn)
        btn = wx.Button(self.panel, wx.ID_OK)
        wx.EVT_BUTTON(self, wx.ID_OK, self._on_ok)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        _sz_main.Add(btnsizer, 0, wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM, 5)

        self.panel.SetSizer(_sz_main)
        _sz_frame = wx.BoxSizer()
        _sz_frame.Add(self.panel, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(_sz_frame)

        self.SetTitle("Loxodo - " + _("Settings"))
        self.Layout()

        self.Fit()
        self.SetMinSize(self.GetSize())

        self.set_initial_focus()
        self.update_fields()

    def _add_a_checkbox(self, parent_sizer, label, extrastyle=0):
        _label = wx.StaticText(self.panel, -1, label, style=wx.ALIGN_RIGHT)
        parent_sizer.Add(_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5)
        control =        wx.CheckBox(self.panel,-1)
        parent_sizer.Add(control, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
        return control

    def _add_a_spincontrol(self, parent_sizer, label, min, max, extrastyle=0):
        _label = wx.StaticText(self.panel, -1, label, style=wx.ALIGN_RIGHT)
        parent_sizer.Add(_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5)
        control = wx.SpinCtrl(self.panel, -1, style=extrastyle, size=(12, -1))
        control.SetRange(min,max)
        parent_sizer.Add(control, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
        return control

    def _add_a_textcontrol(self, parent_sizer, label, default_value, extrastyle=0):
        _label = wx.StaticText(self.panel, -1, label, style=wx.ALIGN_RIGHT)
        parent_sizer.Add(_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5)
        control = wx.TextCtrl(self.panel, -1, default_value, style=extrastyle, size=(128, -1))
        parent_sizer.Add(control, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
        return control

    def _add_a_textbox(self, parent_sizer, label, default_value):
        _label = wx.StaticText(self.panel, -1, label, style=wx.ALIGN_RIGHT)
        parent_sizer.Add(_label, 0, wx.ALL|wx.ALIGN_TOP|wx.ALIGN_RIGHT, 5)
        control = wx.TextCtrl(self.panel, -1, default_value, style=wx.TE_MULTILINE, size=(128, -1))
        parent_sizer.Add(control, 1, wx.ALIGN_TOP|wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
        return control

    def update_fields(self):
        """
        Update fields from source
        """
        self._sc_length.SetValue(config.pwlength)
        self._tc_alphabet.SetValue(config.alphabet)
        self._cb_reduction.SetValue(config.reduction)
        self._search_notes.SetValue(config.search_notes)
        self._search_passwd.SetValue(config.search_passwd)

    def _apply_changes(self, dummy):
        """
        Update source from fields
        """
        config.pwlength = self._sc_length.GetValue()
        config.reduction = self._cb_reduction.GetValue()
        config.search_notes = self._search_notes.GetValue()
        config.search_passwd = self._search_passwd.GetValue()
        config.alphabet = self._tc_alphabet.GetValue()
        config.save()

    def _on_cancel(self, dummy):
        """
        Event handler: Fires when user chooses this button.
        """
        self.EndModal(wx.ID_CANCEL);

    def _on_ok(self, evt):
        """
        Event handler: Fires when user chooses this button.
        """
        self._apply_changes(evt)
        self.EndModal(wx.ID_OK);

    def _on_frame_close(self, dummy):
        """
        Event handler: Fires when user closes the frame
        """
        self.EndModal(wx.ID_CANCEL);

    def _on_escape(self, evt):
        """
        Event handler: Fires when user presses a key
        """
        # If "Escape" was pressed, hide the frame
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL);
            return

        # Ignore all other keys
        evt.Skip()

    def set_initial_focus(self):
        self._sc_length.SetFocus()

