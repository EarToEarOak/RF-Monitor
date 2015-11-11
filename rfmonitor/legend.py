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


class Legend(object):
    def __init__(self, axes, canvas):
        self._axes = axes
        self._canvas = canvas
        self._legend = None
        self._visible = True

    def create(self):
        self._legend = self._axes.legend(fontsize='small')
        if self._legend is not None:
            self._legend.get_frame().set_alpha(0.75)
            self._legend.set_visible(self._visible)

    def get_visible(self):
        return self._visible

    def set_visibile(self, visible):
        self._visible = visible
        if self._legend is not None:
            self._legend.set_visible(self._visible)
            self._canvas.draw()

    def clear(self):
        self._legend = None


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
