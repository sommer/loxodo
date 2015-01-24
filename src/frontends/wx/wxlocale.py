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

from .paths import get_localedir
from ...config import config

_ = wx.GetTranslation
LOXODO_LOCALE = None


def setup_wx_locale():
    """
    Set up internationalization support.
    """
    if 'unicode' not in wx.PlatformInfo:
        print "Warning: You need a unicode build of wxPython to run this application. Continuing anyway."
    try:
        localedir = get_localedir()
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
        global LOXODO_LOCALE
        LOXODO_LOCALE = wx.Locale(langid)
        LOXODO_LOCALE.AddCatalogLookupPathPrefix(localedir)
        LOXODO_LOCALE.AddCatalog(domain)
    except:
        print "Warning: Setting up internationalization support failed. Continuing anyway."

