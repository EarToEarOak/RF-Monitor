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
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter, AutoMinorLocator
from wx import xrc
import wx.lib.newevent

from rfmonitor.constants import BINS, SAMPLE_RATE, MAX_TIMELINE_FPS, TIMELINE_FPS
from rfmonitor.navigation_toolbar import NavigationToolbar
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
        self._monitors = None

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

        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.__on_timer, self._timer)

    def __setup_plot(self):
        figure = Figure()

        self._axes = figure.add_subplot(111)
        self._axes.set_title('Timeline')
        self._axes.set_xlabel('Time')
        self._axes.set_ylabel('Frequency (MHz)')
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
        self._toolbar = NavigationToolbar(self._canvas)

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

    def __on_timer(self, _event):
        self.set_monitors(self._monitors, True)

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

    def set_monitors(self, monitors, isLive):
        self._timer.Stop()
        self._monitors = monitors

        timestamp = time.time()
        if timestamp - self._timestamp > self._delayDraw:
            t1 = time.time()
            self._timestamp = timestamp

            tMin = None
            tMax = None

            height = SAMPLE_RATE / BINS
            height /= 1e6
            self._axes.set_color_cycle(None)

            self.__clear_plots()
            timeNow = epoch2num(time.time())

            for monitor in monitors:
                freq = monitor.get_frequency()
                signals = []
                periods = []

                for period in monitor.get_periods():
                    tStart = epoch2num(period.start)
                    if period.end is not None:
                        tEnd = epoch2num(period.end)
                    else:
                        tEnd = timeNow
                    periods.append([tStart, tEnd - tStart])

                for signal in monitor.get_signals():
                    tStart = epoch2num(signal.start)
                    if signal.end is not None:
                        tEnd = epoch2num(signal.end)
                    else:
                        tEnd = timeNow
                    tMin = min(tMin, tStart)
                    tMax = max(tMax, tEnd)
                    signals.append([tStart, tEnd - tStart])

                colour = self._axes._get_lines.color_cycle.next()
                self._axes.broken_barh(periods, [freq - height / 2, height],
                                       color=colour,
                                       alpha=0.2,
                                       gid='plot')
                self._axes.broken_barh(signals, [freq - height / 2, height],
                                       color=colour,
                                       gid='plot')
                self._axes.axhline(freq,
                                   color=colour,
                                   gid='plot',)

            if isLive:
                tMax = timeNow
                self._axes.axvline(timeNow,
                                   color='black',
                                   linestyle='--',
                                   gid='plot')

            if tMax is None:
                self._axes.set_xlim(timeNow - 1. / 288, timeNow)
                self._axes.autoscale(axis='y')
            else:
                self._axes.set_xlim(tMin, tMax)
                self._axes.autoscale(self._toolbar.get_autoscale())

            self._axes.get_figure().autofmt_xdate()

            self._canvas.draw()

            delay = time.time() - t1
            self._delayDraw += delay * 2.
            self._delayDraw /= 2.
            if self._delayDraw < 1. / MAX_TIMELINE_FPS:
                self._delayDraw = 1. / MAX_TIMELINE_FPS

            if isLive:
                self._timer.Start(1000. / TIMELINE_FPS, True)


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
