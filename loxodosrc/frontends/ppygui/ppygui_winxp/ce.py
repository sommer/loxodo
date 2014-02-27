## Copyright (c) Alexandre Delattre 2008
## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal in the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:

## The above copyright notice and this permission notice shall be
## included in all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
## NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
## LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
## OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
## WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE


from core import *
from config import HIRES_MULT
from controls import Label, Button
from menu import Menu, PopupMenu, MenuWrapper
from boxing import HBox, VBox, Spacer
#from toolbar import ToolBar

class SIPPref:
    '''
    A hidden Window that automatically
    controls the Software Input Panel
    according to the control focused in
    the parent window.
    
    It should be instancied after all
    other controls in the parent window
    '''
    def __init__(self, parent):
        pass
    
def make_sippref(parent):
    CreateWindowEx(0, u"SIPPREF", u"", WS_CHILD, -10, -10, 5, 5, parent._w32_hWnd, IdGenerator.next(), GetModuleHandle(0), 0)
    
class CommandBarItem(GuiObject):
    '''\
    Not implemented yet, will be used for managing the main menubar 
    aka command bar
    '''
    def __init__(self, cb_hWnd, index):
        self.cb_hWnd = cb_hWnd
        self.index = index
        
    def set_text(self, txt):
        tbbi = TBBUTTONINFO()
        tbbi.cbSize = sizeof(tbbi)
        tbbi.dwMask = TBIF_TEXT | 0x80000000
        tbbi.pszText = unicode(txt)
        SendMessage(self.cb_hWnd, WM_USER+64, self.index, byref(tbbi))
    
    def enable(self, val=True):
        tbbi = TBBUTTONINFO()
        tbbi.cbSize = sizeof(tbbi)
        tbbi.dwMask = TBIF_STATE | 0x80000000
        if val:
            tbbi.fsState = TBSTATE_ENABLED
        else:
            tbbi.fsState = TBSTATE_INDETERMINATE
        SendMessage(self.cb_hWnd, WM_USER+64, self.index, byref(tbbi))
    
        
    def disable(self):
        self.enable(False)
        
##class CommandBarAction(CommandBarItem):
##    '''\
##    Not implemented yet, will be used for managing the main menubar 
##    aka command bar
##    '''
##    def __init__(self, cb_hWnd, index, menu_item):
##        CommandBarItem.__init__(self, cb_hWnd, index)
##        self.menu_item = menu_item
##    
##    def bind(self, cb):
##        self.menu_item.bind(cb)   
##        
##class CommandBarMenu(CommandBarItem, MenuWrapper):
##    '''\
##    Not implemented yet, will be used for managing the main menubar 
##    aka command bar
##    '''
##    def __init__(self, cb_hWnd, index, hMenu):
##        CommandBarItem.__init__(self, cb_hWnd, index)
##        MenuWrapper.__init__(self, hMenu)

class CommandBarAction(Button):
    def __init__(self, parent, name, action):
        Button.__init__(self, parent, name, action)

    def bind(self, clicked=None, **kw):
        Button.bind(self, clicked=clicked, **kw)
        
class CommandBarMenuWrapper(Button):
    def __init__(self, parent, title, menu=None):
        Button.__init__(self, parent, title, action=self.on_click)
        self.menu = menu
        
    def on_click(self, ev):
        x, y = self.parent.pos
        dx, dy = self.pos
        self.menu.popup(self, x+dx, y+dy)
    

class CeFrame(Frame):
    '''\
    CeFrame is a frame designed to be a Windows CE compliant window.
    A CeFrame will track the SIP position and size and will automatically
    resize itself to always fit the screen.
    '''
    _dispatchers = {"_activate" : (MSGEventDispatcher, WM_ACTIVATE),
                    "_settingchanged" : (MSGEventDispatcher, WM_SETTINGCHANGE),
                    }
    _dispatchers.update(Frame._dispatchers)

    _w32_window_style = WS_OVERLAPPED
    
    def __init__(self, parent=None, title="PocketPyGui", action=None, menu=None, tab_traversal=True, visible=True, enabled=True, has_sip=True, has_toolbar=False):
        '''\
        Arguments :
            - parent: the parent window of this CeFrame.
            - title: the title as appearing in the title bar.
            - action : a tuple ('Label', callback) .
            - menu : the title of the right menu as a string
                     if not None, the menu can be filled via the cb_menu attribute
                     after CeFrame initialization.
        '''
        Frame.__init__(self, parent, title, tab_traversal=tab_traversal, visible=visible, enabled=enabled, pos=(-1,-1,240, 320))
        self.title_label = Label(self, title=title)

##        if has_ok:
##            self.top_right_button = gui.Button(self, 'Ok', action=lambda ev: self.onok())
##        else:
        self._create_tr_button()

        if action is None:
            self.cb_action = Spacer(0, 0)#Button(self)
        else:
            name, callback = action
            self.cb_action = CommandBarAction(self, name, action=callback)

        self.cb_menu = PopupMenu()
        if menu is None:
            self._cb_menu = Spacer(0, 0)
        else:
            self._cb_menu = CommandBarMenuWrapper(self, menu, self.cb_menu)

        hbox = HBox()
        hbox.add(self.title_label, 1)
        hbox.add(self.top_right_button)

        hbox2 = HBox()
        hbox2.add(self.cb_action, 1)
        hbox2.add(self._cb_menu, 1)
        
        vbox = VBox()
        vbox.add(hbox)
        vbox.add(Spacer())
        vbox.add(hbox2)
        

        self._sizer = vbox
        self.layout()
        InvalidateRect(self._w32_hWnd, 0, 0)

    def _create_tr_button(self):
        self.top_right_button = Button(self, 'X', action=lambda ev: self.close())

    def set_sizer(self, sizer):
        hbox = HBox()
        hbox.add(self.title_label, 1)
        hbox.add(self.top_right_button)

        hbox2 = HBox()
        hbox2.add(self.cb_action, 1)
        hbox2.add(self._cb_menu, 1)
        
        vbox = VBox()
        vbox.add(hbox)
        vbox.add(sizer, 1)
        vbox.add(hbox2)
        

        self._sizer = vbox
        self.layout()
        InvalidateRect(self._w32_hWnd, 0, 0)
        
    def onok(self):
        pass
    
    def show_sipbutton(self, show=True):
        if show:
            SHFullScreen(self._w32_hWnd, SHFS_SHOWSIPBUTTON)
        else:
            SHFullScreen(self._w32_hWnd, SHFS_HIDESIPBUTTON)
        
    def hide_sipbutton(self):
        self.show_sipbutton(False)
