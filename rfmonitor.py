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

from constants import APP_NAME
from main import RfMonitor, FrameMain


if __name__ == '__main__':
    print APP_NAME + "\n"

    app = RfMonitor()
    app.SetClassName(APP_NAME)
    wx.Locale().Init2()
    frame = FrameMain(APP_NAME)

    app.MainLoop()
