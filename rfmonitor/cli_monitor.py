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
from rfmonitor.utils import set_level


class CliMonitor(Monitor):
    def __init__(self,
                 colour, enabled, alert,
                 frequency, threshold,
                 signals, periods):

        Monitor.__init__(self,
                         colour, enabled, alert,
                         frequency, threshold,
                         signals, periods)

        self._isSaved = True

    def set_level(self, level, timestamp, location):
        update = set_level(self._signals,
                           self._levels,
                           location,
                           True,
                           self._threshold,
                           level,
                           timestamp)
        if update:
            self._isSaved = False

        return update

    def get_saved(self):
        return self._isSaved


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
