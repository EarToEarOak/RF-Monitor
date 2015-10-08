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

from wx import xrc
import wx

from constants import LEVEL_MAX, LEVEL_MIN


class WidgetMeter(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(-1, 25), style=wx.SUNKEN_BORDER)

        self._value = LEVEL_MIN
        self._threshold = LEVEL_MIN

        font = self.GetFont()
        font.SetPixelSize((0, 10))
        self.SetFont(font)

        self.Bind(wx.EVT_PAINT, self.__on_paint)
        self.Bind(wx.EVT_SIZE, self.__on_size)

    def __on_paint(self, _event):
        dc = wx.BufferedPaintDC(self)
        w, h = self.GetClientSize()

        dc.SetPen(wx.Pen(wx.WHITE))
        dc.SetBrush(wx.Brush(wx.WHITE))
        dc.DrawRectangle(0, 0, w, h)

        colour = '#4DDB4D' if self._value >= self._threshold else '#FF4D4D'
        dc.SetPen(wx.Pen(colour))
        dc.SetBrush(wx.Brush(colour))
        x = self.__scale_x(self._value, w)
        dc.DrawRectangle(0, 0, x, h)

        dc.SetPen(wx.Pen(wx.BLACK))
        ticks = range(LEVEL_MIN, LEVEL_MAX, 10)
        for tick in ticks:
            if tick not in [LEVEL_MIN, LEVEL_MAX]:
                x = self.__scale_x(tick, w)
                dc.DrawLine(x, 0, x, 5)
                dc.DrawLine(x, h, x, h - 5)

                label = str(tick)
                tW, tH = dc.GetTextExtent(label)
                dc.DrawText(label, x - tW / 2, (h - tH) / 2)

        dc.SetPen(wx.Pen(wx.BLUE, 2, wx.LONG_DASH))
        x = self.__scale_x(self._threshold, w)
        dc.DrawLine(x, 0, x, h)

    def __on_size(self, _event):
        self.Refresh()

    def __scale_x(self, x, w):
        y = (float(w) / (LEVEL_MAX - LEVEL_MIN)) * (x - LEVEL_MIN)

        return y

    def set_level(self, level):
        self._value = level
        self.Refresh()

    def set_threshold(self, threshold):
        self._threshold = threshold
        self.Refresh()


class XrcHandlerMeter(xrc.XmlResourceHandler):
    def CanHandle(self, node):
        return self.IsOfClass(node, 'WidgetMeter')

    def DoCreateResource(self):
        panel = WidgetMeter(self.GetParent())
        self.SetupWindow(panel)
        self.CreateChildren(panel)

        return panel


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
