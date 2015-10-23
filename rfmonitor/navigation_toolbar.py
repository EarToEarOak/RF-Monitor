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

from matplotlib.backends.backend_wx import NavigationToolbar2Wx


class NavigationToolbar(NavigationToolbar2Wx):
    def __init__(self, canvas):
        NavigationToolbar2Wx.__init__(self, canvas)
        self._canvas = canvas
        self._autoScale = True

    def back(self, *args):
        NavigationToolbar2Wx.back(self, *args)
        self._autoScale = False

    def forward(self, *args):
        NavigationToolbar2Wx.forward(self, *args)
        self._autoScale = False

    def home(self, *args):
        NavigationToolbar2Wx.home(self, *args)
        self._autoScale = True

    def press_pan(self, *args):
        NavigationToolbar2Wx.press_pan(self, *args)
        self._autoScale = False

    def press_zoom(self, *args):
        NavigationToolbar2Wx.press_zoom(self, *args)
        self._autoScale = False

    def get_autoscale(self):
        return self._autoScale


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
