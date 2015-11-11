#! /usr/bin/env python
#
#
# RF Monitor
#
#
# Copyright 2015 Al Brown
#
# RF signal monitor
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import matplotlib
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
import wx


class NavigationToolbar(NavigationToolbar2Wx):
    def __init__(self, canvas, legend):
        NavigationToolbar2Wx.__init__(self, canvas)
        self._canvas = canvas
        self._legend = legend
        self._autoScale = True

        if matplotlib.__version__ >= '1.2':
            panId = self.wx_ids['Pan']
        else:
            panId = self.FindById(self._NTB2_PAN).GetId()
        self.ToggleTool(panId, True)
        self.pan()

        checkLegend = wx.CheckBox(self, label='Legend')
        checkLegend.SetValue(legend.get_visible())
        self.AddControl(checkLegend)
        self.Bind(wx.EVT_CHECKBOX, self.__on_legend, checkLegend, id)

        if wx.__version__ >= '2.9.1':
            self.AddStretchableSpace()
        else:
            self.AddSeparator()

        self._textCursor = wx.StaticText(self, style=wx.ALL | wx.ALIGN_RIGHT)
        font = self._textCursor.GetFont()
        font.MakeSmaller()
        font.SetFamily(wx.FONTFAMILY_TELETYPE)
        self._textCursor.SetFont(font)
        dc = wx.ScreenDC()
        dc.SetFont(font)
        w, _h = dc.GetTextExtent(' ' * 18)
        self._textCursor.SetSize((w, -1))

        self.AddControl(self._textCursor)

        self.Realize()

    def __on_legend(self, event):
        self._legend.set_visibile(event.IsChecked())

    def back(self, *args):
        NavigationToolbar2Wx.back(self, *args)
        self._autoScale = False

    def forward(self, *args):
        NavigationToolbar2Wx.forward(self, *args)
        self._autoScale = False

    def home(self, *args):
        NavigationToolbar2Wx.home(self, *args)
        self._autoScale = True

    def press_pan(self, *args):
        NavigationToolbar2Wx.press_pan(self, *args)
        self._autoScale = False

    def press_zoom(self, *args):
        NavigationToolbar2Wx.press_zoom(self, *args)
        self._autoScale = False

    def get_autoscale(self):
        return self._autoScale

    def set_cursor_text(self, text):
        self._textCursor.SetLabel(text)


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
