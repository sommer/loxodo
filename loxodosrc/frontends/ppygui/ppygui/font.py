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

from w32api import *
from config import HIRES

CreateFontIndirect=windll.coredll.CreateFontIndirectW

class LOGFONT(Structure):
    _fields_ = [("lfHeight", LONG),
                ("lfWidth", LONG),                
                ("lfEscapement", LONG),
                ("lfOrientation", LONG),
                ("lfWeight", LONG),
                ("lfItalic", BYTE),
                ("lfUnderline", BYTE),
                ("lfStrikeOut", BYTE),
                ("lfCharSet", BYTE),
                ("lfOutPrecision", BYTE),
                ("lfClipPrecision", BYTE),
                ("lfQuality", BYTE), 
                ("lfPitchAndFamily", BYTE),
                ("lfFaceName", TCHAR * 32)]

def rgb(r, g, b):
    return r+(g<<8)+(b<<16)
    
class Font(object):
        
    def __init__(self, name='Tahoma', size=9, charset=None,
                 bold=False, italic=False, underline=False, color=(0,0,0) ):
        
        height = int(-size*96/72.0)
        if HIRES :
            height *= 2
            
        lf = LOGFONT()
        lf.lfHeight = height
        if name: lf.lfFaceName = name
        if charset: lf.lfCharSet = self.charsetToInt( charset )
        if bold: lf.lfWeight = 700
        if italic: lf.lfItalic = 1
        if underline : lf.lfUnderline = 1
        self._hFont = CreateFontIndirect(byref(lf))
        self._color = rgb(*color)
        
    def __del__(self):
        DeleteObject(self._hFont)

    def charsetToInt( charset ):
        """
        Map a charset name to a win32 charset identifier for font selection.
        For convenience, the charset passed in can already be a win32 charset int,
        in which case, it is returned unchanged.
        """
        if type(charset) == type(""):
            if CharsetMap.has_key( charset.lower() ):
                return CharsetMap[ charset.lower() ]
        elif type(charset) == type(1):
            return charset
        # don't cause problems, return default charset
        return 1    # default charset

    charsetToInt = staticmethod( charsetToInt )
        
DefaultFont = Font(size=8)
ButtonDefaultFont = Font(size=8, bold=True)

# these are defined in Wingdi.h
CharsetMap = { 'ansi':              0,
               'iso-8859-1':        0,      # actually this is ansi, a superset of iso-8859-1
               'default':           1,
               'symbol':            2,
               'mac':               77,
               'japanese':          128,
               'shift-jis':         128,
               'hangul':            129,
               'hangeul':           129,
               'euc-kr':            129,
               'johab':             130,
               'chinese_gb2312':    134,
               'gb2312':            134,
               'chinese_big5':      136,
               'big5':              136,
               'greek':             161,
               'iso-8859-7':        161,
               'turkish':           162,
               'iso-8859-9':        162,
               'vietnamese':        163,
               'hebrew':            177,
               'iso-8859-8':        177,
               'arabic':            178,
               'iso-8859-6':        178,
               'baltic':            186,
               'iso-8859-4':        186,
               'russian':           204,
               'iso-8859-5':        204,
               'thai':              222,
               'easteurope':        238,
               'iso-8859-2':        238,
               'oem':               255
               }

 	  	 
