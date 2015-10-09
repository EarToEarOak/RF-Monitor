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

from constants import LEVEL_MIN, LEVEL_MAX
from ui import load_ui
from widget_meter import XrcHandlerMeter
from xrchandlers import XrcHandlerNumCtrl


class PanelMonitor(wx.Panel):
    def __init__(self, parent):
        self._parent = parent
        self._isRecording = False
        self._isSaved = True
        self._timestamp = None
        self._signals = []

        pre = wx.PrePanel()
        self._ui = load_ui('PanelMonitor.xrc')

        handlerNumCtrl = XrcHandlerNumCtrl()
        handlerMeter = XrcHandlerMeter()
        self._ui.AddHandler(handlerNumCtrl)
        self._ui.AddHandler(handlerMeter)

        self._ui.LoadOnPanel(pre, parent, 'PanelMonitor')
        self.PostCreate(pre)

        self._checkEnable = xrc.XRCCTRL(pre, 'checkEnable')
        self._choiceFreq = xrc.XRCCTRL(pre, 'choiceFreq')
        self._textSignals = xrc.XRCCTRL(pre, 'textSignals')
        # TODO: hackish
        for child in self.GetChildren():
            if child.Name == 'panel':
                self._meterLevel = child
        self._sliderThreshold = xrc.XRCCTRL(pre, 'sliderThreshold')
        self._buttonDel = xrc.XRCCTRL(pre, 'buttonDel')

        self._sliderThreshold.SetMin(LEVEL_MIN)
        self._sliderThreshold.SetMax(LEVEL_MAX)
        self._meterLevel.set_threshold(self._sliderThreshold.GetValue())

        self.__set_signals()

        self._on_del = None

        self.Bind(wx.EVT_SLIDER, self.__on_threshold, self._sliderThreshold)
        self.Bind(wx.EVT_CHECKBOX, self.__on_enable, self._checkEnable)
        self.Bind(wx.EVT_BUTTON, self.__on_del, self._buttonDel)

    def __on_threshold(self, _event):
        threshold = self._sliderThreshold.GetValue()
        self._meterLevel.set_threshold(threshold)

    def __on_enable(self, _event):
        self._buttonDel.Enable(not self.is_enabled())

    def __on_del(self, _event):
        if not self.get_saved():
            resp = wx.MessageBox('''Remove monitor?\n'''
                                 '''The recording on this channel will be lost''',
                                 'Warning',
                                 wx.OK | wx.CANCEL | wx.ICON_WARNING)
            if resp != wx.OK:
                return
        self._on_del(self)

    def __set_signals(self):
        signals = len(self._signals)
        label = 'Recorded: {:4d}'.format(signals)
        if not self._isSaved:
            label += '*'
        self._textSignals.SetLabel(label)
        self._choiceFreq.Enable(signals < 1)

    def set_callback(self, on_del):
        self._on_del = on_del

    def set_enabled(self, enabled):
        self._checkEnable.SetValue(enabled)
        self.__on_enable(None)

    def is_enabled(self):
        return self._checkEnable.IsChecked()

    def set_freqs(self, freqs):
        freqs = map(str, freqs)
        self._choiceFreq.Clear()
        self._choiceFreq.AppendItems(freqs)
        self._choiceFreq.SetSelection(len(freqs) / 2)

    def set_freq(self, freq):
        freqs = map(float, self._choiceFreq.GetItems())
        try:
            self._choiceFreq.SetSelection(freqs.index(freq))
        except ValueError:
            self._choiceFreq.SetSelection(len(freqs) / 2)
        self._signals = []
        self._isSaved = True
        self.__set_signals()

    def get_freq(self):
        index = self._choiceFreq.GetCurrentSelection()
        return float(self._choiceFreq.GetItems()[index])

    def set_threshold(self, threshold):
        self._meterLevel.set_threshold(threshold)
        self._sliderThreshold.SetValue(threshold)

    def get_threshold(self):
        return self._sliderThreshold.GetValue()

    def set_level(self, level, timestamp):
        self._meterLevel.set_level(level)
        threshold = self._sliderThreshold.GetValue()
        if self._isRecording:
            if self._timestamp is None:
                if level >= threshold:
                    self._timestamp = timestamp
            else:
                if level < threshold:
                    self._signals.append((self._timestamp, timestamp))
                    self._timestamp = None
                    self._isSaved = False
                    self.__set_signals()

    def set_recording(self, isRecording):
        self._isRecording = isRecording

    def set_signals(self, signals):
        self._signals = signals

    def get_signals(self):
        return self._signals

    def clear_signals(self):
        self._signals = []
        self._timestamp = None
        self._isSaved = True
        self.__set_signals()

    def set_saved(self):
        self._isSaved = True

    def get_saved(self):
        return self._isSaved


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
