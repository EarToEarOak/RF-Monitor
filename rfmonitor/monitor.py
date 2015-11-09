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
from rfmonitor.signals import Period


LEVELS_LEN = MAX_LEVELS_TIME * SAMPLE_RATE / SAMPLES


class Monitor(object):
    def __init__(self,
                 colour, enabled, alert,
                 frequency, threshold,
                 signals, periods):

        self._colour = colour
        self._enabled = enabled
        self._alert = alert
        self._freq = frequency
        self._threshold = threshold
        self._signals = signals
        self._levels = collections.deque(maxlen=round(LEVELS_LEN))
        self._periods = periods

    def get_colour(self):
        return self._colour

    def get_enabled(self):
        return self._enabled

    def get_alert(self):
        return self._alert

    def get_frequency(self):
        return self._freq

    def get_threshold(self):
        return self._threshold

    def get_signals(self):
        return self._signals

    def get_periods(self):
        return self._periods

    def get_levels(self):
        return self._levels

    def set_colour(self, colour):
        self._colour = colour

    def set_enabled(self, enabled):
        self._enabled = enabled

    def set_alert(self, alert):
        self._alert = alert

    def set_frequency(self, frequency):
        self._freq = frequency

    def set_threshold(self, threshold):
        self._threshold = threshold

    def set_signals(self, signals):
        self._signals = signals

    def set_levels(self, levels):
        self._levels = levels

    def set_periods(self, periods):
        self._periods = periods

    def start_period(self, timestamp):
        period = Period(timestamp)
        self._periods.append(period)

    def end_period(self, timestamp):
        self._periods[-1].end = timestamp


if __name__ == '__main__':
    exit(1)
    print 'Please run rfmonitor.py'
