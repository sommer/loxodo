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
import os
import __builtin__

from loadframe import LoadFrame

def _configure_locale():
    """
    Set up internationalization support.
    """
    if 'unicode' not in wx.PlatformInfo:
        print "Warning: You need a unicode build of wxPython to run this application. Continuing anyway."
    try:
        localedir = os.path.join(os.path.dirname(__file__), "..", "locale")
        domain = "loxodo"

        from locale import getdefaultlocale
        langid = wx.LANGUAGE_DEFAULT
        try:
            (lang_name, dummy) = getdefaultlocale()
        except ValueError:
            pass
        else:
            if lang_name:
                langid = wx.Locale.FindLanguageInfo(lang_name).Language
        mylocale = wx.Locale(langid)
        mylocale.AddCatalogLookupPathPrefix(localedir)
        mylocale.AddCatalog(domain)
        __builtin__.__dict__['_'] = wx.GetTranslation
        __builtin__.__dict__['LOXODO_LOCALE'] = mylocale
    except:
        print "Warning: Setting up internationalization support failed. Continuing anyway."
        __builtin__.__dict__['_'] = lambda x: x


app = wx.PySimpleApp(0)
_configure_locale()
wx.InitAllImageHandlers()
main = LoadFrame(None, -1, "")
app.SetTopWindow(main)
main.Show()

dial = wx.MessageDialog(main,
                                    _('This is an unstable preview version of Loxodo. Prior to opening any file with this program, please create a backup and store it in a safe place - this version *will* destroy the original copy.'),
                                    _('Version warning'),
                                    wx.OK | wx.ICON_WARNING
                                    )
dial.ShowModal()
dial.Destroy()

app.MainLoop()

