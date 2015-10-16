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

import numpy

from rfmonitor.signals import Signal


def set_level(signals, levels, location,
              isRecording, threshold, level, timestamp):
    updated = False
    currentSignal = None

    if isRecording:
        if len(signals) and signals[-1].end is None:
            currentSignal = signals[-1]

        if currentSignal is None:
            if level is not None and level >= threshold:
                currentSignal = Signal(start=timestamp, location=location)
                signals.append(currentSignal)
                updated = True
        else:
            if level is None or level < threshold:
                strength = numpy.mean(levels)
                levels.clear()
                currentSignal.end = timestamp
                currentSignal.level = strength
                updated = True

        if level is not None and level >= threshold:
            levels.append(level)

    if updated:
        return currentSignal

    return None


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
