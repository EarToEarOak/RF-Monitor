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

from wx import xrc
import wx

from rfmonitor.constants import LEVEL_MIN, LEVEL_MAX
from rfmonitor.events import post_event, Event, Events
from rfmonitor.monitor import Monitor
from rfmonitor.ui import load_ui
from rfmonitor.utils import set_level
from rfmonitor.widget_meter import XrcHandlerMeter, WidgetMeter
from rfmonitor.xrchandlers import XrcHandlerNumCtrl


class PanelMonitor(Monitor, wx.Panel):
    def __init__(self, parent, eventHandler):
        Monitor.__init__(self, None, False, False, None, None, [], [])

        self._eventHandler = eventHandler
        self._isRecording = False
        self._isRunning = False
        self._isLow = True
        self._colours = []

        pre = wx.PrePanel()
        self._ui = load_ui('PanelMonitor.xrc')

        handlerNumCtrl = XrcHandlerNumCtrl()
        handlerMeter = XrcHandlerMeter()
        self._ui.AddHandler(handlerNumCtrl)
        self._ui.AddHandler(handlerMeter)

        self._ui.LoadOnPanel(pre, parent, 'PanelMonitor')
        self.PostCreate(pre)

        self._panelColour = xrc.XRCCTRL(pre, 'panelColour')
        self._checkEnable = xrc.XRCCTRL(pre, 'checkEnable')
        self._checkAlert = xrc.XRCCTRL(pre, 'checkAlert')
        self._choiceFreq = xrc.XRCCTRL(pre, 'choiceFreq')
        self._textSignals = xrc.XRCCTRL(pre, 'textSignals')
        # TODO: hackish
        for child in self.GetChildren():
            if isinstance(child, WidgetMeter):
                self._meterLevel = child
        self._sliderThreshold = xrc.XRCCTRL(pre, 'sliderThreshold')
        self._buttonDel = xrc.XRCCTRL(pre, 'buttonDel')

        self._sliderThreshold.SetMin(LEVEL_MIN)
        self._sliderThreshold.SetMax(LEVEL_MAX)
        self._threshold = self._sliderThreshold.GetValue()
        self._meterLevel.set_threshold(self._threshold)

        self.__set_records()

        self._on_del = None

        self._panelColour.Bind(wx.EVT_LEFT_UP, self.__on_colour)
        self.Bind(wx.EVT_CHECKBOX, self.__on_enable, self._checkEnable)
        self.Bind(wx.EVT_CHECKBOX, self.__on_alert, self._checkAlert)
        self.Bind(wx.EVT_CHOICE, self.__on_freq, self._choiceFreq)
        self.Bind(wx.EVT_SLIDER, self.__on_threshold, self._sliderThreshold)
        self.Bind(wx.EVT_BUTTON, self.__on_del, self._buttonDel)

    def __on_colour(self, _event):
        colourData = wx.ColourData()
        colourData.SetChooseFull(True)
        colourData.SetColour([level * 255 for level in self._colour])
        for i in range(len(self._colours)):
            colour = [level * 255 for level in self._colours[i]]
            colourData.SetCustomColour(i, colour)

        dlg = wx.ColourDialog(self, colourData)
        if dlg.ShowModal() == wx.ID_OK:
            colour = dlg.GetColourData().GetColour()
            colour = [level / 255. for level in colour]
            self.set_colour(colour)
            event = Event(Events.CHANGED)
            post_event(self._eventHandler, event)

    def __on_enable(self, _event):
        enabled = self._checkEnable.IsChecked()
        self.set_enabled(enabled)
        timestamp = time.time()
        if self._isRecording and self._enabled:
            self.start_period(timestamp)
        elif self._isRecording and not self._enabled:
            self.end_period(timestamp)

        event = Event(Events.CHANGED)
        post_event(self._eventHandler, event)

    def __on_alert(self, _event):
        self._alert = self._checkAlert.IsChecked()

        event = Event(Events.CHANGED)
        post_event(self._eventHandler, event)

    def __on_freq(self, event):
        self._freq = float(event.GetString())

        event = Event(Events.CHANGED)
        post_event(self._eventHandler, event)

    def __on_threshold(self, _event):
        self._threshold = self._sliderThreshold.GetValue()
        self._meterLevel.set_threshold(self._threshold)

        event = Event(Events.CHANGED)
        post_event(self._eventHandler, event)

    def __on_del(self, _event):
        if len(self._signals):
            resp = wx.MessageBox('''Remove monitor?\n'''
                                 '''The recording on this monitor will be lost''',
                                 'Warning',
                                 wx.OK | wx.CANCEL | wx.ICON_WARNING)
            if resp != wx.OK:
                return
        self._on_del(self)

    def __enable_freq(self):
        self._choiceFreq.Enable(not self._isRecording and not
                                len(self._signals))

    def __set_records(self):
        signals = len(self._signals)
        label = 'Recorded: {:4d}'.format(signals)
        self._textSignals.SetLabel(label)
        self.__enable_freq()

    def get_colour(self):
        return self._colour

    def set_callback(self, on_del):
        self._on_del = on_del

    def set_enabled(self, enabled):
        self._enabled = enabled
        self._checkEnable.SetValue(enabled)
        self._buttonDel.Enable(not self._enabled)
        self.__enable_freq()
        if not self._enabled:
            self._meterLevel.set_level(LEVEL_MIN)

    def set_alert(self, alert):
        self._alert = alert
        self._checkAlert.SetValue(alert)

    def set_freqs(self, freqs):
        freqs = map(str, freqs)
        self._choiceFreq.Clear()
        self._choiceFreq.AppendItems(freqs)
        index = len(freqs) / 2
        self._freq = float(freqs[index])
        self._choiceFreq.SetSelection(len(freqs) / 2)

    def set_freq(self, freq):
        freqs = map(float, self._choiceFreq.GetItems())
        try:
            self._choiceFreq.SetSelection(freqs.index(freq))
            self._freq = freq
        except ValueError:
            self._choiceFreq.SetSelection(len(freqs) / 2)
            index = self._choiceFreq.GetSelection()
            self._freq = float(self._choiceFreq.GetItems()[index])
        self._signals = []
        self.__set_records()

    def set_threshold(self, threshold):
        self._threshold = threshold
        self._meterLevel.set_threshold(threshold)
        self._sliderThreshold.SetValue(threshold)

    def set_level(self, level, timestamp, location):
        self._meterLevel.set_level(level)
        threshold = self._threshold

        signal = set_level(self._signals,
                           self._levels,
                           location,
                           self._isRecording,
                           threshold,
                           level,
                           timestamp)

        if signal is not None:
            self.__set_records()

        if level >= threshold and self._isLow:
            self._isLow = False
            if self._alert:
                event = Event(Events.MON_ALERT)
                post_event(self._eventHandler, event)
        elif level < threshold:
            self._isLow = True

        return signal

    def set_recording(self, isRecording, timestamp):
        self._isRecording = isRecording
        self.__enable_freq()
        if isRecording and self._enabled:
            self.start_period(timestamp)
        elif not self._isRecording and self._enabled:
            self.end_period(timestamp)

    def set_signals(self, signals):
        self._signals = signals
        self.__set_records()

    def set_colour(self, colour):
        self._colour = colour
        if colour is not None:
            wxColour = [level * 255 for level in colour]
            self._panelColour.SetBackgroundColour(wxColour)
            self._panelColour.Refresh()

    def set_colours(self, colours):
        self._colours = colours

    def clear(self):
        self._signals = []
        self._periods = []
        self.__set_records()


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
