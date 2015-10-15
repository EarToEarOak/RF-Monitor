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


class Signal(object):
    def __init__(self=None, start=None, end=None, level=None, location=None):
        self.start = start
        self.end = end
        self.level = level
        self.location = location

    @staticmethod
    def from_list(signal):
        return Signal(*signal)

    def to_list(self):
        return [self.start, self.end, self.level, self.location]


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
