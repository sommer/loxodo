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
from wx.lib import filebrowsebutton

from .wxlocale import _
from .vaultframe import VaultFrame
from ...vault import Vault
from ...config import config
from .paths import get_resourcedir


class LoadFrame(wx.Frame):
    """
    Displays the "welcome" dialog which lets the user open a Vault.
    """
    def __init__(self, *args, **kwds):
        # begin wxGlade: ChooseVaultFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        self._lb_passwd = wx.StaticText(self.panel_1, -1, _("Password") + ":")
        self._tc_passwd = wx.TextCtrl(self.panel_1, -1, "", style=wx.TE_PASSWORD)
        self.bitmap_1 = wx.StaticBitmap(self.panel_1, -1, wx.Bitmap(os.path.join(get_resourcedir(), "loxodo-icon.png"), wx.BITMAP_TYPE_ANY))
        self._fb_filename = filebrowsebutton.FileBrowseButtonWithHistory(self.panel_1, -1, size=(450, -1),  changeCallback = self._on_pickvault, labelText = _("Vault") + ":")
        if (config.recentvaults):
            self._fb_filename.SetHistory(config.recentvaults, 0)
        self.static_line_1 = wx.StaticLine(self.panel_1, -1)

        self.SetTitle("Loxodo - " + _("Open Vault"))

        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)

        sizer_3.Add(self.bitmap_1, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        sizer_3.Add(self._fb_filename, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT|wx.RIGHT, 5)

        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5.Add(self._lb_passwd, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
        sizer_5.Add(self._tc_passwd, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
        sizer_3.Add(sizer_5, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)

        sizer_3.Add(self.static_line_1, 0, wx.TOP|wx.EXPAND, 10)

        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(self.panel_1, wx.ID_NEW)
        wx.EVT_BUTTON(self, wx.ID_NEW, self._on_new)
        btnsizer.Add(btn, 0, wx.TOP | wx.RIGHT, 10)
        btn = wx.Button(self.panel_1, wx.ID_OPEN)
        wx.EVT_BUTTON(self, wx.ID_OPEN, self._on_open)
        btn.SetDefault()
        btnsizer.Add(btn, 0, wx.TOP | wx.RIGHT, 10)
        sizer_3.Add(btnsizer, 0, wx.ALIGN_RIGHT | wx.BOTTOM, 5)

        self.panel_1.SetSizer(sizer_3)
        sizer_2.Add(self.panel_1, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer_2)
        sizer_2.Fit(self)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.SetMaxSize((-1, self.GetSize().height))
        self._tc_passwd.SetFocus()

    def _on_pickvault(self, evt):
        pass

    def _on_new(self, dummy):
        password = self._tc_passwd.GetValue().encode('latin1', 'replace')

        filename = self._fb_filename.GetValue()
        wildcard = "|".join((_("Vault") + " (*.psafe3)", "*.psafe3", _("All files") + " (*.*)", "*.*"))
        dialog = wx.FileDialog(self, message = _("Save new Vault as..."), defaultFile = filename, wildcard = wildcard, style = wx.SAVE | wx.OVERWRITE_PROMPT)
        if dialog.ShowModal() != wx.ID_OK:
            return
        filename = dialog.GetPath()
        dialog.Destroy()

        Vault.create(password, filename=filename)
        self._fb_filename.SetValue(filename)

        dial = wx.MessageDialog(self,
                                _('A new Vault has been created using the given password. You can now proceed to open the Vault.'),
                                _('Vault Created'),
                                wx.OK | wx.ICON_INFORMATION
                                )
        dial.ShowModal()
        dial.Destroy()
        self._tc_passwd.SetFocus()
        self._tc_passwd.SelectAll()

    def _on_open(self, dummy):
        try:
            password = self._tc_passwd.GetValue().encode('latin1', 'replace')
            vaultframe = VaultFrame(None, -1, "")
            vaultframe.open_vault(self._fb_filename.GetValue(), password)
            config.recentvaults.insert(0, self._fb_filename.GetValue())
            config.save()
            self.Hide()
            vaultframe.Show()
            self.Destroy()
        except Vault.BadPasswordError:
            vaultframe.Destroy()
            dial = wx.MessageDialog(self,
                                    _('The given password does not match the Vault'),
                                    _('Bad Password'),
                                    wx.OK | wx.ICON_ERROR
                                    )
            dial.ShowModal()
            dial.Destroy()
            self._tc_passwd.SetFocus()
            self._tc_passwd.SelectAll()
        except Vault.VaultVersionError:
            vaultframe.Destroy()
            dial = wx.MessageDialog(self,
                                    _('This is not a PasswordSafe V3 Vault'),
                                    _('Bad Vault'),
                                    wx.OK | wx.ICON_ERROR
                                    )
            dial.ShowModal()
            dial.Destroy()
        except Vault.VaultFormatError:
            vaultframe.Destroy()
            dial = wx.MessageDialog(self,
                                    _('Vault integrity check failed'),
                                    _('Bad Vault'),
                                    wx.OK | wx.ICON_ERROR
                                    )
            dial.ShowModal()
            dial.Destroy()

