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

import os
import sys

from wx import xrc, Sound


def __get_ui_dir():
    scriptDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    resDir = os.path.join(scriptDir, 'rfmonitor', 'ui')

    return resDir


def load_ui(filename):
    ui = os.path.join(__get_ui_dir(), filename)
    return xrc.XmlResource(ui)


def load_sound(filename):
    sound = os.path.join(__get_ui_dir(), filename)
    return Sound(sound)


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
