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
from ce import CeFrame
from controls import Button
 
EnableWindow = windll.user32.EnableWindow
IsDialogMessage = windll.user32.IsDialogMessageW

class Dialog(CeFrame):    
    #_w32_window_class = "DIALOG"
    #_w32_window_style = WS_MAXIMIZE
    #_w32_window_style_ex = 0x10000
    
    def __init__(self, title, action=None, menu=None, visible=False, enabled=True, has_sip=True, has_ok=True):
        self.has_ok = has_ok
        CeFrame.__init__(self, None, title, action=action, menu=menu, visible=visible, enabled=enabled, has_sip=has_sip)
        self.bind(close=self._onclose)
        #self.has_ok = has_ok
        self.poppingup = False
        

    def _create_tr_button(self):
        if self.has_ok:
            self.top_right_button = Button(self, 'Ok', action=lambda ev: self.onok())
        else:
            CeFrame._create_tr_button(self)
            

            
    def popup(self, parent=None):
        self._parent = parent
        
        self.show()
        self.bringtofront()
        if self._parent :
            self._parent.disable()
            #self._parent.hide()
        
        self.poppingup = True
        while self.poppingup:
            msg = MSG()
            lpmsg = byref(msg)
            if GetMessage(lpmsg, 0, 0, 0):
                
                if IsDialogMessage(self._w32_hWnd, lpmsg):  
                    continue
                TranslateMessage(lpmsg)
                DispatchMessage(lpmsg)
            else :
                PostQuitMessage()
                return
                
        return self.ret_code
        
    def end(self, code):
        self.ret_code = code
        self.poppingup = False
        if self._parent is not None:
            self._parent.enable()
            #self._parent.show()
            self._parent.bringtofront()
            self._parent.focus()
        self.hide()
        
    def onok(self):
        self.end('ok')
        
    def oncancel(self):
        self.end('cancel')
        
    def _onclose(self, event):
#        if self._parent is not None:

#            self._parent.enable()

#            self._parent.show()

#            self._parent.bringtofront()
        self.end('cancel')
