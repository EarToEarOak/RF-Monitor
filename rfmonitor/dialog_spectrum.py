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

import time

import matplotlib
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from wx import xrc
import wx.lib.newevent

from rfmonitor.constants import MAX_SPECTRUM_FPS
from rfmonitor.navigation_toolbar import NavigationToolbar
from rfmonitor.ui import load_ui

EventSpectrumClose, EVT_SPECTRUM_CLOSE = wx.lib.newevent.NewEvent()


class DialogSpectrum(wx.Dialog):
    def __init__(self, parent, freqs):
        self._parent = parent
        self._spectrum = None
        self._toolbar = None
        self._textFreq = None
        self._timestamp = 0
        self._delayDraw = 1. / MAX_SPECTRUM_FPS
        self._axes = None
        self._canvas = None
        self._freqs = freqs

        pre = wx.PreDialog()
        self._ui = load_ui('DialogSpectrum.xrc')
        self._ui.LoadOnDialog(pre, parent, 'DialogSpectrum')
        self.PostCreate(pre)

        self._panelPlot = xrc.XRCCTRL(pre, 'panelPlot')
        self._buttonClose = xrc.XRCCTRL(pre, 'buttonClose')
        self.Bind(wx.EVT_BUTTON, self.__on_close, self._buttonClose)

        self.Bind(wx.EVT_CLOSE, self.__on_close)

        self.__setup_plot()
        self.__setup_toolbar()

        sizer = self._panelPlot.GetSizer()
        sizer.Add(self._canvas, 1, wx.ALL | wx.GROW)
        sizer.Add(self._toolbar, 0, wx.LEFT | wx.EXPAND)
        self.Fit()

    def __setup_plot(self):
        figure = Figure(facecolor='lightgrey')

        self._axes = figure.add_subplot(111)
        self._axes.set_title('Spectrum')
        self._axes.set_xlabel('Frequency (MHz)')
        self._axes.set_ylabel('Level (dB)')
        self._axes.autoscale_view(True, True, True)
        self._axes.grid(True)

        self._spectrum, = self._axes.plot([], [], 'b-')

        self._canvas = FigureCanvas(self._panelPlot, -1, figure)
        self._canvas.mpl_connect('motion_notify_event', self.__on_motion)

    def __setup_toolbar(self):
        self._toolbar = NavigationToolbar(self._canvas)

        if wx.__version__ >= '2.9.1':
            self._toolbar.AddStretchableSpace()
        else:
            self._toolbar.AddSeparator()
        self._textFreq = wx.StaticText(self._toolbar, label='          ')
        font = self._textFreq.GetFont()
        font.SetFamily(wx.FONTFAMILY_TELETYPE)
        self._textFreq.SetFont(font)
        self._toolbar.AddControl(self._textFreq)
        self._toolbar.Realize()

    def __on_motion(self, event):
        label = ''
        if event.xdata is not None:
            freq = min(self._freqs, key=lambda x: abs(x - event.xdata))
            label = '{: 8.4f}MHz'.format(freq)
        self._textFreq.SetLabel(label)

    def __on_close(self, _event):
        evt = EventSpectrumClose()
        wx.PostEvent(self._parent, evt)
        self.Destroy()

    def __clear_lines(self):
        for child in self._axes.get_children():
            gid = child.get_gid()
            if gid is not None and gid == 'line':
                child.remove()

    def set_spectrum(self, freqs, levels, monitors, noise):
        timestamp = time.time()
        self._freqs = freqs
        if timestamp - self._timestamp > self._delayDraw:
            t1 = time.time()
            self._timestamp = timestamp

            self.__clear_lines()
            self._axes.axhline(noise,
                               color='black',
                               ls='--',
                               gid='line')
            for monitor in monitors:
                colour = monitor.get_colour()
                self._axes.axvline(monitor.get_frequency(),
                                   color=colour,
                                   dashes=[2, 1],
                                   gid='line')
                self._axes.axhline(monitor.get_threshold(),
                                   color=colour,
                                   dashes=[2, 1],
                                   gid='line')

            self._spectrum.set_data(freqs, levels)
            self._axes.relim()
            self._axes.autoscale_view(True, True, True)
            self._axes.autoscale(self._toolbar.get_autoscale())

            self._canvas.draw()
            delay = time.time() - t1
            self._delayDraw += delay * 2.
            self._delayDraw /= 2.
            if self._delayDraw < 1. / MAX_SPECTRUM_FPS:
                self._delayDraw = 1. / MAX_SPECTRUM_FPS

    def clear_spectrum(self):
        self.__clear_lines()
        self._canvas.draw()


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
