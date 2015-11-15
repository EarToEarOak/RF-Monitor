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

import wx
from wx.lib import masked
from wx.lib.agw import aui

from rfmonitor.events import Event, Events, post_event
from rfmonitor.utils_wx import get_text_size


class Toolbar(aui.AuiToolBar):
    def __init__(self, parent):
        aui.AuiToolBar.__init__(self, parent)
        self._parent = parent

        self._numFreq = masked.NumCtrl(self,
                                       integerWidth=4,
                                       fractionWidth=3,
                                       value=1,
                                       min=1,
                                       max=9999,
                                       limited=True)
        self._numFreq.SetToolTipString('Centre frequency (MHz)')
        self.AddControl(self._numFreq)
        self.AddLabel(wx.ID_ANY, 'MHz',
                      get_text_size('MHz',
                                    self._numFreq.GetFont())[0])

        self._choiceGain = wx.Choice(self)
        self._choiceGain.SetToolTipString('Gain (dB)')
        self.AddControl(self._choiceGain)
        self.AddLabel(wx.ID_ANY, 'dB',
                      get_text_size('dB',
                                    self._numFreq.GetFont())[0])

        self._numCal = masked.NumCtrl(self,
                                      integerWidth=4,
                                      fractionWidth=3,
                                      value=0,
                                      min=-1000,
                                      max=1000,
                                      allowNegative=True,
                                      limited=True)
        self._numCal.SetToolTipString('Calibration (ppm)')
        self.AddControl(self._numCal)
        self.AddLabel(wx.ID_ANY, 'ppm',
                      get_text_size('ppm',
                                    self._numFreq.GetFont())[0])

        self.AddSeparator()

        self._spinDyn = wx.SpinCtrl(self,
                                    min=0,
                                    max=99,
                                    size=(50, -1))
        self._spinDyn.SetToolTipString('Dynamic noise level (percentile)')
        self.AddControl(self._spinDyn)

        self.AddSeparator()

        self._buttonStart = wx.Button(self, label='Start')
        self._buttonStart.SetToolTipString('Start monitoring')
        self.AddControl(self._buttonStart)

        self._buttonRec = wx.ToggleButton(self, label='Record')
        self._buttonRec.SetToolTipString('Toggle recording')
        self.AddControl(self._buttonRec)

        self._buttonStop = wx.Button(self, label='Stop')
        self._buttonStop.SetToolTipString('Stop monitoring')
        self.AddControl(self._buttonStop)

        self.AddSeparator()
        self.AddStretchSpacer()

        self._buttonAdd = wx.Button(self, label='+', style=wx.BU_EXACTFIT)
        self._buttonAdd.SetToolTipString('Add monitor')
        self.AddControl(self._buttonAdd)

        self.Realize()

        self._on_freq = None
        self._on_start = None
        self._on_rec = None
        self._on_stop = None
        self._on_add = None

        self._dynPercentile = 0

        self.Bind(masked.EVT_NUM, self.__on_freq, self._numFreq)
        self.Bind(wx.EVT_CHOICE, self.__on_change, self._choiceGain)
        self.Bind(masked.EVT_NUM, self.__on_change, self._numCal)
        self.Bind(wx.EVT_SPINCTRL, self.__on_dynamic, self._spinDyn)
        self.Bind(wx.EVT_BUTTON, self.__on_start, self._buttonStart)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.__on_rec, self._buttonRec)
        self.Bind(wx.EVT_BUTTON, self.__on_stop, self._buttonStop)
        self.Bind(wx.EVT_BUTTON, self.__on_add, self._buttonAdd)

    def __on_change(self, _event=None):
        event = Event(Events.CHANGED)
        post_event(self._parent, event)

    def __on_freq(self, _event):
        self._on_freq(self._numFreq.GetValue())
        self.__on_change()

    def __on_dynamic(self, _event):
        self._dynPercentile = self._spinDyn.GetValue()
        self.__on_change()

    def __on_start(self, _event):
        self.enable_start(False)
        self._on_start()

    def __on_rec(self, _event):
        self.enable_start(False)
        recording = self._buttonRec.GetValue()
        self._on_rec(recording)

    def __on_stop(self, _event):
        if self.is_recording():
            self._buttonRec.SetValue(False)
            self.__on_rec(None)
        self.enable_start(True)
        self._on_stop()

    def __on_add(self, _event):
        self._on_add()

    def set_callbacks(self,
                      on_freq,
                      on_start,
                      on_rec,
                      on_stop,
                      on_add):
        self._on_freq = on_freq
        self._on_start = on_start
        self._on_rec = on_rec
        self._on_stop = on_stop
        self._on_add = on_add

    def is_recording(self):
        return self._buttonRec.GetValue()

    def enable_freq(self, enable):
        self._numFreq.Enable(enable)

    def enable_start(self, enable):
        self._choiceGain.Enable(enable)
        self._numCal.Enable(enable)
        self._buttonStart.Enable(enable)
        self._buttonStop.Enable(not enable)

    def set_freq(self, freq):
        self.SetEvtHandlerEnabled(False)
        self._numFreq.SetValue(freq)
        self.SetEvtHandlerEnabled(True)

    def get_freq(self):
        return self._numFreq.GetValue()

    def set_gains(self, gains):
        gains = map(str, gains)
        self._choiceGain.Clear()
        self._choiceGain.AppendItems(gains)
        self._choiceGain.SetSelection(len(gains) / 2)

    def set_gain(self, gain):
        self.SetEvtHandlerEnabled(False)
        gains = map(float, self._choiceGain.GetItems())
        try:
            self._choiceGain.SetSelection(gains.index(gain))
        except ValueError:
            self._choiceGain.SetSelection(len(gains) / 2)
        self.SetEvtHandlerEnabled(True)

    def get_gain(self):
        index = self._choiceGain.GetSelection()
        return float(self._choiceGain.GetItems()[index])

    def set_cal(self, cal):
        self.SetEvtHandlerEnabled(False)
        self._numCal.SetValue(cal)
        self.SetEvtHandlerEnabled(True)

    def get_cal(self):
        return int(self._numCal.GetValue())

    def set_dynamic_percentile(self, percentile):
        self._dynPercentile = percentile
        self._spinDyn.SetValue(percentile)

    def get_dynamic_percentile(self):
        return self._dynPercentile


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
