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


import Queue

import wx


EVENT_THREAD = wx.NewId()


class Events(object):
    SCAN_ERROR, SCAN_DATA, \
        SERVER_ERROR, \
        GPS_ERROR, GPS_WARN, GPS_TIMEOUT, GPS_LOC, GPS_SATS, \
        CHANGED, \
        PUSH_ERROR, \
        MON_ALERT = range(11)


class Event(wx.PyEvent):
    def __init__(self, eventType, **kwargs):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVENT_THREAD)
        self.type = eventType
        self.data = kwargs


def post_event(destination, event):
    if isinstance(destination, Queue.Queue):
        destination.put(event)
    elif isinstance(destination, wx.EvtHandler):
        wx.PostEvent(destination, event)


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
