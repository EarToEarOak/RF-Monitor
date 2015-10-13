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

import collections

from rfmonitor.constants import MAX_LEVELS_TIME, SAMPLE_RATE, SAMPLES
from rfmonitor.utils import set_level


class CliMonitor(object):
    def __init__(self, frequency, threshold, enabled, signals):
        self._freq = frequency
        self._threshold = threshold
        self._enabled = enabled
        self._timestamp = None
        self._signals = signals
        self._isSaved = True
        levelsLength = MAX_LEVELS_TIME * SAMPLE_RATE / SAMPLES
        self._levels = collections.deque(maxlen=round(levelsLength))

    def is_enabled(self):
        return self._enabled

    def get_freq(self):
        return self._freq

    def get_threshold(self):
        return self._threshold

    def set_level(self, level, timestamp, location):
        update, self._timestamp = set_level(self._signals,
                                            self._levels,
                                            location,
                                            True,
                                            self._threshold,
                                            level,
                                            timestamp,
                                            self._timestamp)
        if update:
            self._isSaved = False

        return update

    def get_signals(self):
        return self._signals

    def get_saved(self):
        return self._isSaved



if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
