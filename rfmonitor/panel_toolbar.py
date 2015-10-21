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
from wx.lib import masked

from rfmonitor.ui import load_ui
from rfmonitor.xrchandlers import XrcHandlerNumCtrl


class PanelToolbar(wx.Panel):
    def __init__(self, parent):
        self._parent = parent

        pre = wx.PrePanel()
        self._ui = load_ui('PanelToolbar.xrc')

        handlerNumCtrl = XrcHandlerNumCtrl()
        self._ui.AddHandler(handlerNumCtrl)

        self._ui.LoadOnPanel(pre, parent, 'PanelToolbar')
        self.PostCreate(pre)

        self._numFreq = xrc.XRCCTRL(pre, 'ctrlFreq')
        self._choiceGain = xrc.XRCCTRL(pre, 'choiceGain')
        self._buttonStart = xrc.XRCCTRL(pre, 'buttonStart')
        self._buttonRec = xrc.XRCCTRL(pre, 'buttonRecord')
        self._buttonStop = xrc.XRCCTRL(pre, 'buttonStop')
        self._buttonAdd = xrc.XRCCTRL(pre, 'buttonAdd')

        self._numFreq.SetMin(1)
        self._numFreq.SetMax(9999)
        self._numFreq.SetAllowNone(False)
        self._numFreq.SetLimited(True)

        self._on_freq = None
        self._on_start = None
        self._on_rec = None
        self._on_stop = None
        self._on_add = None

        self.Bind(masked.EVT_NUM, self.__on_freq, self._numFreq)
        self.Bind(wx.EVT_BUTTON, self.__on_start, self._buttonStart)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.__on_rec, self._buttonRec)
        self.Bind(wx.EVT_BUTTON, self.__on_stop, self._buttonStop)
        self.Bind(wx.EVT_BUTTON, self.__on_add, self._buttonAdd)

    def __on_freq(self, _event):
        self._on_freq(self._numFreq.GetValue())

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
        self._buttonStart.Enable(enable)
        self._buttonStop.Enable(not enable)
        self._buttonAdd.Enable(enable)

    def set_freq(self, freq):
        self._numFreq.SetValue(freq)

    def get_freq(self):
        return self._numFreq.GetValue()

    def set_gains(self, gains):
        gains = map(str, gains)
        self._choiceGain.Clear()
        self._choiceGain.AppendItems(gains)
        self._choiceGain.SetSelection(len(gains) / 2)

    def set_gain(self, gain):
        gains = map(float, self._choiceGain.GetItems())
        try:
            self._choiceGain.SetSelection(gains.index(gain))
        except ValueError:
            self._choiceGain.SetSelection(len(gains) / 2)

    def get_gain(self):
        index = self._choiceGain.GetSelection()
        return float(self._choiceGain.GetItems()[index])


class XrcHandlerToolbar(xrc.XmlResourceHandler):
    def CanHandle(self, node):
        return self.IsOfClass(node, 'PanelToolbar')

    def DoCreateResource(self):
        panel = PanelToolbar(self.GetParent())
        self.SetupWindow(panel)
        self.CreateChildren(panel)

        return panel


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
