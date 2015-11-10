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
import threading
from urllib2 import URLError
import urllib2

from rfmonitor.events import Event, Events, post_event


class Push(object):
    def __init__(self, handler):
        self._handler = handler

    def __send(self, uri, data):
        req = urllib2.Request(uri)
        req.add_header('Content-Type', 'application/json')

        try:
            urllib2.urlopen(req, data)
        except ValueError as error:
            event = Event(Events.PUSH_ERROR, msg=error.message)
            post_event(self._handler, event)
        except URLError as error:
            event = Event(Events.PUSH_ERROR, msg=error.reason.strerror)
            post_event(self._handler, event)

    def send(self, uri, data):
        thread = threading.Thread(target=self.__send, args=(uri, data,))
        thread.daemon = True
        thread.start()


if __name__ == '__main__':
    exit(1)
    print 'Please run rfmonitor.py'
