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

APP_NAME = 'RF Monitor'

LEVEL_MIN = -100
LEVEL_MAX = 20

SAMPLE_RATE = 2.4e6
SAMPLES = 256 * 1024

MAX_SPECTRUM_FPS = 25
MAX_TIMELINE_FPS = 5
TIMELINE_FPS = 1

MAX_LEVELS_TIME = 300  # 5 minutes

ALERT_LENGTH = 0.1

BINS = 256  # SAMPLE_RATE/BINS = 9.375kHz

GPS_RETRY = 5

if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
