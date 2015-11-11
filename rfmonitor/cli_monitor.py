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


from rfmonitor.monitor import Monitor


class CliMonitor(Monitor):
    def __init__(self,
                 colour, enabled, alert,
                 frequency, threshold, dynamic,
                 signals, periods):

        Monitor.__init__(self,
                         colour, enabled, alert,
                         frequency, threshold, dynamic,
                         signals, periods)

        self._isSaved = True

    def set_level(self, level, timestamp, location):
        signal = Monitor.set_level(self, level, timestamp, location)
        if signal is not None:
            self._isSaved = False

        return signal

    def get_saved(self):
        return self._isSaved


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
