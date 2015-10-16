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
from threading import Timer
import time

import numpy
import wx

from rfmonitor.cli_monitor import CliMonitor
from rfmonitor.constants import GPS_RETRY
from rfmonitor.events import Events
from rfmonitor.file import load_recordings, save_recordings, format_recording
from rfmonitor.gps import GpsDevice, Gps
from rfmonitor.receive import Receive
from rfmonitor.server import Server
from rfmonitor.settings import Settings


class Cli(wx.EvtHandler):
    def __init__(self, args):
        wx.EvtHandler.__init__(self)
        self._monitors = []
        self._freqs = []
        self._location = None
        self._settings = Settings()
        self._filename = args.file
        self._gpsPort = args.port
        self._gpsBaud = args.baud
        self._json = args.json
        self._receive = None
        self._cancel = False

        self._queue = Queue.Queue()

        self.__open()
        self.__add_monitors()

        self._signal = signal.signal(signal.SIGINT, self.__on_exit)

        self._server = Server(self._queue)

        self._gps = None
        self.__start_gps()

        self.__start()

        while not self._cancel:
            if not self._queue.empty():
                self.__on_event()

        self.__std_out('Exiting')
        self._receive.stop()
        self.__stop_gps()
        if self._server is not None:
            self._server.stop()
        timestamp = time.time()
        for monitor in self._monitors:
            monitor.set_level(None, timestamp, None)

        if not self.__is_saved():
            self.__std_out('Saving')
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
        self.__std_out('Monitors:')
        self.__std_out(', '.join(freqs) + 'MHz\n')

    def __start_gps(self):
        gpsDevice = GpsDevice()
        if self._gpsPort is not None:
            gpsDevice.port = self._gpsPort
        if self._gpsBaud is not None:
            gpsDevice.baud = self._gpsBaud
        if self._gpsPort is not None:
            self._gps = Gps(self._queue, gpsDevice)

    def __stop_gps(self):
        if self._gps is not None:
            self._gps.stop()

    def __restart_gps(self):
        timer = Timer(GPS_RETRY, self.__start_gps)
        timer.start()

    def __start(self):
        self.__std_out('Monitoring starting with:')
        self.__std_out('Base frequancy: %s'% self._settings.get_freq()
        self.__std_out('Gain: %s' % self._settings.get_gain()
        self._receive = Receive(self._queue,
                                self._settings.get_freq(),
                                self._settings.get_gain())

    def __std_out(self, message):
        if not self._json:
            sys.stdout.write(message + '\n')

    def __std_err(self, message):
        if not self._json:
            sys.stderr.write(message + '\n')

    def __on_exit(self, _signal=None, _frame=None):
        signal.signal(signal.SIGINT, self._signal)
        self._cancel = True

    def __on_event(self):
        event = self._queue.get()
        if event.type == Events.SCAN_ERROR:
            self.__on_scan_error(event.data)
        elif event.type == Events.SCAN_DATA:
            self.__on_scan_data(event.data)
        elif event.type == Events.SERVER_ERROR:
            self.__on_server_error(event.data)
        elif event.type == Events.GPS_ERROR:
            self.__std_err(event.data['msg'])
            self.__restart_gps()
        elif event.type == Events.GPS_WARN:
            self.__std_err(event.data['msg'])
        elif event.type == Events.GPS_TIMEOUT:
            self.__std_err(event.data['msg'])
            self.__restart_gps()
        elif event.type == Events.GPS_LOC:
            self._location = event.data['loc']
        else:
            time.sleep(0.01)

    def __on_scan_error(self, event):
        self.__std_err(event['msg'])
        self._cancel = True

    def __on_scan_data(self, event):
        levels = numpy.log10(event['l'])
        levels *= 10

        for monitor in self._monitors:
            freq = monitor.get_freq()
            if monitor.is_enabled():
                index = numpy.where(freq == event['f'])[0]
                signal = monitor.set_level(levels[index][0],
                                           event['timestamp'],
                                           self._location)

            if signal is not None:
                if signal.end is not None:
                    recording = format_recording(freq, signal)
                    if self._server is not None:
                        self._server.send(recording)
                    if self._json:
                        sys.stdout.write(recording + '\n')

    def __on_server_error(self, event):
        self.__std_err(event['msg'])
        self._server = None


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
