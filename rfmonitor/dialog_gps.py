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

from rfmonitor.ui import load_ui


class DialogGps(wx.Dialog):
    def __init__(self, parent, gps):
        self._gps = gps

        pre = wx.PreDialog()
        self._ui = load_ui('DialogGps.xrc')
        self._ui.LoadOnDialog(pre, parent, 'DialogGps')
        self.PostCreate(pre)

        self._checkEnable = xrc.XRCCTRL(pre, 'checkEnable')
        self._choicePort = xrc.XRCCTRL(pre, 'choicePort')
        self._choiceBaud = xrc.XRCCTRL(pre, 'choiceBaud')
        self._buttonOk = xrc.XRCCTRL(pre, 'wxID_OK')

        self._checkEnable.SetValue(gps.enabled)
        self._choicePort.AppendItems(gps.get_ports())
        port = self._choicePort.FindString(gps.port)
        if port == wx.NOT_FOUND:
            port = 0
        self._choicePort.SetSelection(port)
        self._choiceBaud.AppendItems(map(str, gps.get_bauds()))
        baud = self._choiceBaud.FindString(str(gps.baud))
        if baud == wx.NOT_FOUND:
            baud = 0
        self._choiceBaud.SetSelection(baud)

        self.Bind(wx.EVT_BUTTON, self.__on_ok, self._buttonOk)

    def __on_ok(self, _event):
        self._gps.enabled = self._checkEnable.GetValue()
        port = self._choicePort.GetSelection()
        self._gps.port = self._choicePort.GetItems()[port]
        baud = self._choiceBaud.GetSelection()
        self._gps.baud = int(self._choiceBaud.GetItems()[baud])

        self.EndModal(wx.ID_OK)


if __name__ == '__main__':
    exit(1)
    print 'Please run rfmonitor.py'
