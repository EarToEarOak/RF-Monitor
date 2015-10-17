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

LEVELS_LEN = MAX_LEVELS_TIME * SAMPLE_RATE / SAMPLES


class Monitor(object):
    def __init__(self, enabled, frequency, threshold, signals):
        self._enabled = enabled
        self._freq = frequency
        self._threshold = threshold
        self._signals = signals
        self._levels = collections.deque(maxlen=round(LEVELS_LEN))

    def get_enabled(self):
        return self._enabled

    def get_frequency(self):
        return self._freq

    def get_threshold(self):
        return self._threshold

    def get_signals(self):
        return self._signals

    def get_levels(self):
        return self._levels

    def set_enabled(self, enabled):
        self._enabled = enabled

    def set_frequency(self, frequency):
        self._freq = frequency

    def set_threshold(self, threshold):
        self._threshold = threshold

    def set_signals(self, signals):
        self._signals = signals

    def set_levels(self, levels):
        self._levels = levels


if __name__ == '__main__':
    exit(1)
    print 'Please run rfmonitor.py'
