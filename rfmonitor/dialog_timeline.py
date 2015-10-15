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

import datetime
import time

import matplotlib
matplotlib.use('WXAgg')

from matplotlib.dates import epoch2num, num2epoch, AutoDateLocator, \
    AutoDateFormatter
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter, AutoMinorLocator
from wx import xrc
import wx.lib.newevent

from rfmonitor.constants import MAX_TIMELINE_FPS, BINS, SAMPLE_RATE
from rfmonitor.ui import load_ui


EventTimelineClose, EVT_TIMELINE_CLOSE = wx.lib.newevent.NewEvent()


class DialogTimeline(wx.Dialog):
    def __init__(self, parent):
        self._parent = parent
        self._toolbar = None
        self._textFreq = None
        self._timestamp = 0
        self._delayDraw = 1. / MAX_TIMELINE_FPS
        self._axes = None
        self._canvas = None

        pre = wx.PreDialog()
        self._ui = load_ui('DialogTimeline.xrc')
        self._ui.LoadOnDialog(pre, parent, 'DialogTimeline')
        self.PostCreate(pre)

        self._panelPlot = xrc.XRCCTRL(pre, 'panelPlot')
        self._button_Close = xrc.XRCCTRL(pre, 'buttonClose')
        self.Bind(wx.EVT_BUTTON, self.__on_close, self._button_Close)

        self.Bind(wx.EVT_CLOSE, self.__on_close)

        self.__setup_plot()
        self.__setup_toolbar()

        sizer = self._panelPlot.GetSizer()
        sizer.Add(self._canvas, 1, wx.ALL | wx.GROW)
        sizer.Add(self._toolbar, 0, wx.LEFT | wx.EXPAND)
        self.Fit()

    def __setup_plot(self):
        figure = Figure()

        self._axes = figure.add_subplot(111)
        self._axes.set_title('Timeline')
        self._axes.set_xlabel('Time')
        self._axes.set_ylabel('Frequency (MHz)')
        self._axes.autoscale(True)
        self._axes.grid(True)
        locator = AutoDateLocator()
        formatter = AutoDateFormatter(locator)
        self._axes.xaxis.set_major_formatter(formatter)
        self._axes.xaxis.set_major_locator(locator)
        formatter = ScalarFormatter(useOffset=False)
        self._axes.yaxis.set_major_formatter(formatter)
        self._axes.yaxis.set_minor_locator(AutoMinorLocator(10))

        self._canvas = FigureCanvas(self._panelPlot, -1, figure)
        self._canvas.mpl_connect('motion_notify_event', self.__on_motion)

    def __setup_toolbar(self):
        self._toolbar = NavigationToolbar2Wx(self._canvas)

        if wx.__version__ >= '2.9.1':
            self._toolbar.AddStretchableSpace()
        else:
            self._toolbar.AddSeparator()
        self._textFreq = wx.StaticText(self._toolbar, label='                ')
        font = self._textFreq.GetFont()
        font.SetFamily(wx.FONTFAMILY_MODERN)
        self._textFreq.SetFont(font)
        self._toolbar.AddControl(self._textFreq)
        self._toolbar.Realize()

    def __on_motion(self, event):
        label = ''
        if event.xdata is not None and event.xdata >= 1:
            timestamp = num2epoch(event.xdata)
            label = datetime.datetime.fromtimestamp(timestamp).strftime('%c')
        self._textFreq.SetLabel(label)

    def __on_close(self, _event):
        evt = EventTimelineClose()
        wx.PostEvent(self._parent, evt)
        self.Destroy()

    def __clear_plots(self):
        for child in self._axes.get_children():
            gid = child.get_gid()
            if gid is not None and gid == 'plot':
                child.remove()

    def set_signals(self, allSignals):
        timestamp = time.time()
        if timestamp - self._timestamp > self._delayDraw:
            t1 = time.time()
            self._timestamp = timestamp

            height = SAMPLE_RATE / BINS
            height /= 1e6
            self._axes.set_color_cycle(None)

            self.__clear_plots()
            hasData = False
            for freq, signals in allSignals:
                if len(signals):
                    hasData = True
                barsX = []
                for start, end, _level, _location in signals:
                    tStart = epoch2num(start)
                    tEnd = epoch2num(end)
                    barsX.append([tStart, tEnd - tStart])
                colour = self._axes._get_lines.color_cycle.next()
                self._axes.broken_barh(barsX, [freq - height / 2, height],
                                       color=colour,
                                       gid='plot')
                self._axes.axhspan(freq, freq, color=colour)

            if not hasData:
                now = epoch2num(time.time())
                self._axes.set_xlim(now, now + 1)

            self._axes.get_figure().autofmt_xdate()
            self._axes.relim()
            self._canvas.draw()

            delay = time.time() - t1
            self._delayDraw += delay * 2.
            self._delayDraw /= 2.
            if self._delayDraw < 1. / MAX_TIMELINE_FPS:
                self._delayDraw = 1. / MAX_TIMELINE_FPS


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
