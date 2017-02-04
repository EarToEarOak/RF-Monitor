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

from rfmonitor.constants import LEVEL_MAX, LEVEL_MIN


TICK_SIZE_MAJ = 4
TICK_SIZE_MIN = 2
THRES_SIZE = 4


class WidgetMeter(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(-1, 25), style=wx.SUNKEN_BORDER)

        self._value = LEVEL_MIN
        self._threshold = LEVEL_MIN
        self._noise = None

        font = self.GetFont()
        font.SetFamily(wx.FONTFAMILY_MODERN)
        self.SetFont(font)

        self.SetMinSize((250, 25))

        self.Bind(wx.EVT_PAINT, self.__on_paint)
        self.Bind(wx.EVT_SIZE, self.__on_size)

        try:
            self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        except AttributeError:
            pass

    def __on_paint(self, _event):
        pdc = wx.BufferedPaintDC(self)
        try:
            dc = wx.GCDC(pdc)
        except:
            dc = pdc

        w, h = self.GetClientSize()

        font = self.GetFont()
        font.SetPixelSize((0, h - (TICK_SIZE_MAJ * 2)))
        dc.SetFont(font)

        dc.SetPen(wx.Pen(wx.WHITE))
        dc.SetBrush(wx.Brush(wx.WHITE))
        dc.DrawRectangle(0, 0, w, h)

        colour = '#4DDB4D' if self._value >= self._threshold else '#FF4D4D'
        dc.SetPen(wx.Pen(colour))
        dc.SetBrush(wx.Brush(colour))
        x = self.__scale_x(self._value, w)
        dc.DrawRectangle(0, 0, x, h)

        colour = wx.Colour(0x80, 0x80, 0xFF, 128)
        dc.SetPen(wx.Pen(colour, 2))
        dc.SetBrush(wx.Brush(colour))
        x = round(self.__scale_x(self._threshold, w))
        dc.DrawPolygon([(x - THRES_SIZE, 0),
                        (x + THRES_SIZE, 0),
                        (x, THRES_SIZE)])
        dc.DrawPolygon([(x - THRES_SIZE, h),
                        (x + THRES_SIZE, h),
                        (x, h - THRES_SIZE)])
        dc.DrawLine(x, THRES_SIZE, x, h - THRES_SIZE)

        if self._noise is not None:
            dc.SetPen(wx.Pen('#8080FF', 1))
            x = self.__scale_x(self._noise, w)
            dc.DrawRectangle(0, TICK_SIZE_MAJ * 3 / 2.,
                             x, h - (TICK_SIZE_MAJ * 3))

        colour = wx.Colour(0x4d, 0x4d, 0x4d)
        dc.SetPen(wx.Pen(colour))
        dc.SetTextForeground(colour)
        ticks = range(LEVEL_MIN, LEVEL_MAX, 10)
        for tick in ticks:
            if tick not in [LEVEL_MIN, LEVEL_MAX]:
                x = self.__scale_x(tick, w)
                dc.DrawLine(x, 0, x, TICK_SIZE_MAJ)
                dc.DrawLine(x, h, x, h - TICK_SIZE_MAJ)

                label = str(tick)
                tW, tH = dc.GetTextExtent(label)
                dc.DrawText(label, x - tW / 2, (h - tH) / 2)
        ticks = range(LEVEL_MIN, LEVEL_MAX, 1)
        for tick in ticks:
            if tick not in [LEVEL_MIN, LEVEL_MAX]:
                x = self.__scale_x(tick, w)
                dc.DrawLine(x, 0, x, TICK_SIZE_MIN)
                dc.DrawLine(x, h, x, h - TICK_SIZE_MIN)

    def __on_size(self, _event):
        self.Refresh()

    def __scale_x(self, x, w):
        y = (float(w) / (LEVEL_MAX - LEVEL_MIN)) * (x - LEVEL_MIN)

        return y

    def set_level(self, level):
        if level is not None:
            self._value = level
            self.Refresh()

    def set_threshold(self, threshold, refresh=True):
        self._threshold = threshold
        if refresh:
            self.Refresh()

    def set_noise(self, noise):
        self._noise = noise


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
