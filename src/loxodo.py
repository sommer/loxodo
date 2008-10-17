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

from loadframe import LoadFrame

app = wx.PySimpleApp(0)
wx.InitAllImageHandlers()
main = LoadFrame(None, -1, "")
app.SetTopWindow(main)
main.Show()

dial = wx.MessageDialog(main,
                                    'This is an unstable preview version of Loxodo. Prior to opening any file with this program, please create a backup and store it in a safe place - this version *will* destroy the original copy.',
                                    'Version warning',
                                    wx.OK | wx.ICON_WARNING
                                    )
dial.ShowModal()
dial.Destroy()

app.MainLoop()

