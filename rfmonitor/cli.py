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
import signal
import sys
import time

import numpy
import wx

from rfmonitor.cli_monitor import CliMonitor
from rfmonitor.events import Events
from rfmonitor.file import load_recordings, save_recordings
from rfmonitor.receive import Receive
from rfmonitor.server import Server
from rfmonitor.settings import Settings


class Cli(wx.EvtHandler):
    def __init__(self, filename):
        wx.EvtHandler.__init__(self)
        self._monitors = []
        self._freqs = []
        self._settings = Settings()
        self._filename = filename
        self._receive = None
        self._cancel = False

        self._queue = Queue.Queue()

        self.__open()
        self.__add_monitors()

        self._signal = signal.signal(signal.SIGINT, self.__on_exit)

        self._server = Server(self._queue)

        self.__start()

        while not self._cancel:
            if not self._queue.empty():
                self.__on_event()

        print 'Exiting'
        self._receive.stop()
        if self._server is not None:
            self._server.stop()

        if not self.__is_saved():
            print 'Saving'
            self.__save()

    def __open(self):
        load_recordings(self._filename,
                        self._settings)

    def __save(self):
        save_recordings(self._filename,
                        self._settings)

    def __is_saved(self):
        for monitor in self._monitors:
            if not monitor.get_saved():
                return False

        return True

    def __add_monitors(self):
        freqs = []
        for monitor in self._settings.get_monitors():
            freq = monitor.freq
            freqs.append(freq)
            cliMonitor = CliMonitor(monitor.freq,
                                    monitor.threshold,
                                    monitor.enabled,
                                    monitor.signals)
            self._monitors.append(cliMonitor)

        freqs = map(str, freqs)
        print 'Monitors:'
        print ', '.join(freqs) + 'MHz\n'

    def __start(self):
        print 'Monitoring'
        self._receive = Receive(self._queue,
                                self._settings.get_freq(),
                                self._settings.get_gain())

    def __on_exit(self, _signal=None, _frame=None):
        signal.signal(signal.SIGINT, self._signal)
        self._cancel = True

    def __on_event(self):
        event = self._queue.get()
        if event.type == Events.SCAN_ERROR:
            self.__on_scan_error(event.data)
        elif event.type == Events.SCAN_DATA:
            self.__on_scan_data(event.data)
        if event.type == Events.SERVER_ERROR:
            self.__on_server_error(event.data)
        else:
            time.sleep(0.01)

    def __on_scan_error(self, event):
        sys.stderr.write(event['msg'])
        exit(1)

    def __on_scan_data(self, event):
        levels = numpy.log10(event['l'])
        levels *= 10

        for monitor in self._monitors:
            freq = monitor.get_freq()
            if monitor.is_enabled():
                index = numpy.where(freq == event['f'])[0]
                update = monitor.set_level(levels[index][0],
                                           event['timestamp'])

            if update and self._server is not None:
                self._server.send(freq, update)

    def __on_server_error(self, event):
        sys.stderr.write(event['msg'])
        self._server = None


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
