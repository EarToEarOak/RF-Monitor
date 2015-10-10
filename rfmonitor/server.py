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


import json
import select
import socket
import threading

from rfmonitor.events import Event, Events, post_event


PORT = 15622


class Server(threading.Thread):
    def __init__(self, eventHandler):
        threading.Thread.__init__(self)
        self.name = 'Server'
        self._eventHandler = eventHandler

        self._client = None
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self._server.bind(('', PORT))
            self._server.listen(5)
        except socket.error:
            event = Event(Events.SCAN_ERROR, msg='Could not start server')
            post_event(eventHandler, event)
            return

        self._cancel = False
        self.start()

    def run(self):
        while not self._cancel:
            if self._client is None:
                endpoints = [self._server]
            else:
                endpoints = [self._server, self._client]

            read, _write, error = select.select(endpoints, [], [], 0.5)

            for sock in read:
                if sock is self._server:
                    try:
                        client, _addr = self._server.accept()
                        if self._client is not None:
                            self._client.close()
                        self._client = client
                    except socket.error:
                        self._client = None

            for sock in error:
                if sock is self._client:
                    self._client = None
                sock.close()

    def send(self, freq, signal):
        data = {freq * 1e6: signal}

        if self._client is not None:
            try:
                self._client.sendall(json.dumps(data))
                self._client.sendall('\r\n')
            except socket.error:
                self._client.close()
                self._client = None

    def stop(self):
        self._cancel = True
        self._server.close()


if __name__ == '__main__':
    exit(1)
    print 'Please run rfmonitor.py'
