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


def set_level(signals, levels, location,
              isRecording, threshold, level, timestamp, lastTime):
    if isRecording:
        if lastTime is None:
            if level >= threshold:
                lastTime = timestamp
        else:
            if level < threshold:
                strength = numpy.mean(levels)
                levels.clear()
                signal = (lastTime, timestamp, strength, location)
                signals.append(signal)
                lastTime = None
                return signal, lastTime
        if level >= threshold:
            levels.append(level)
    return False, lastTime


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
