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


class DialogAbout(wx.Dialog):
    def __init__(self, parent):
        pre = wx.PreDialog()
        self._ui = load_ui('DialogAbout.xrc')
        self._ui.LoadOnDialog(pre, parent, 'DialogAbout')
        self.PostCreate(pre)

        self._buttonOk = xrc.XRCCTRL(pre, 'buttonOk')
        self.Bind(wx.EVT_BUTTON, self.__on_ok, self._buttonOk)

    def __on_ok(self, _event):
        self.Destroy()


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
