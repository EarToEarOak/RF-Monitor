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
import time

from serial.serialutil import SerialException
import serial.tools.list_ports

from rfmonitor.events import Event, Events, post_event


TIMEOUT = 15


class GpsDevice(object):
    BITS = [serial.FIVEBITS, serial.SIXBITS, serial.SEVENBITS,
            serial.EIGHTBITS]
    PARITIES = [serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD,
                serial.PARITY_MARK, serial.PARITY_SPACE]
    STOPS = [serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE,
             serial.STOPBITS_TWO]

    def __init__(self):
        self.enabled = False
        self.port = ''
        self.baud = 115200
        self.bits = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stops = serial.STOPBITS_ONE
        self.soft = False

    def get_ports(self):
        ports = [port[0] for port in serial.tools.list_ports.comports()]
        return ports

    def get_bauds(self):
        return list(serial.Serial.BAUDRATES)


class Gps(threading.Thread):
    def __init__(self, eventHandler, gpsDevice):
        threading.Thread.__init__(self)
        self.name = 'GPS'

        self._gpsDevice = gpsDevice
        self._eventHandler = eventHandler

        self._comm = None
        self._timeout = None
        self._cancel = False

        self._sats = {}

        self.start()

    def __timeout(self):
        self.stop()
        event = Event(Events.GPS_TIMEOUT, msg='GPS timeout')
        post_event(self._eventHandler, event)

    def __serial_read(self):
        isSentence = False
        sentence = ''
        while not self._cancel:
            data = self._comm.read(1)
            if data:
                self._timeout.reset()
                if data == '$':
                    isSentence = True
                    continue
                if data == '\r' or data == '\n':
                    isSentence = False
                    if sentence:
                        yield sentence
                        sentence = ''
                if isSentence:
                    sentence += data
            else:
                time.sleep(0.1)

    def __checksum(self, data):
        checksum = 0
        for char in data:
            checksum ^= ord(char)
        return "{0:02X}".format(checksum)

    def __global_fix(self, data):
        if data[6] in ['1', '2']:
            lat = self.__coord(data[2], data[3])
            lon = self.__coord(data[4], data[5])

            event = Event(Events.GPS_LOC, loc=(lat, lon))
            post_event(self._eventHandler, event)

    def __sats(self, data):
        message = int(data[1])
        messages = int(data[1])
        viewed = int(data[3])

        if message == 1:
            self._sats.clear()

        blocks = (len(data) - 4) / 4
        for i in range(0, blocks):
            sat = int(data[4 + i * 4])
            level = data[7 + i * 4]
            used = True
            if level == '':
                level = None
                used = False
            else:
                level = int(level)
            self._sats[sat] = {'Level': level,
                               'Used': used}

        if message == messages and len(self._sats) == viewed:
            event = Event(Events.GPS_SATS, sats=self._sats)
            post_event(self._eventHandler, event)

    def __coord(self, coord, orient):
        pos = None

        if '.' in coord:
            if coord.index('.') == 4:
                try:
                    degrees = int(coord[:2])
                    minutes = float(coord[2:])
                    pos = degrees + minutes / 60.
                    if orient == 'S':
                        pos = -pos
                except ValueError:
                    pass
            elif coord.index('.') == 5:
                try:
                    degrees = int(coord[:3])
                    minutes = float(coord[3:])
                    pos = degrees + minutes / 60.
                    if orient == 'W':
                        pos = -pos
                except ValueError:
                    pass

        return pos

    def __open(self):
        self._timeout = Timeout(self.__timeout)
        self._comm = serial.Serial(self._gpsDevice.port,
                                   baudrate=self._gpsDevice.baud,
                                   bytesize=self._gpsDevice.bits,
                                   parity=self._gpsDevice.parity,
                                   stopbits=self._gpsDevice.stops,
                                   xonxoff=self._gpsDevice.soft,
                                   timeout=0)

    def __read(self):
        for resp in self.__serial_read():
            nmea = resp.split('*')
            if len(nmea) == 2:
                data = nmea[0].split(',')
                if data[0] in ['GPGGA', 'GPGSV']:
                    checksum = self.__checksum(nmea[0])
                    if checksum == nmea[1]:
                        if data[0] == 'GPGGA':
                            self.__global_fix(data)
                        elif data[0] == 'GPGSV':
                            self.__sats(data)
                    else:
                        warn = 'Invalid checksum for {} sentence'.format(data[0])
                        event = Event(Events.GPS_WARN, msg=warn)
                        post_event(self._eventHandler, event)

    def __close(self):
        if self._timeout is not None:
            self._timeout.cancel()
        if self._comm is not None:
            self._comm.close()

    def run(self):
        try:
            self.__open()
            self.__read()
        except SerialException as error:
            event = Event(Events.GPS_ERROR, msg=error.message)
            post_event(self._eventHandler, event)
        except OSError as error:
            event = Event(Events.GPS_ERROR, msg=error)
            post_event(self._eventHandler, event)
        except ValueError as error:
            event = Event(Events.GPS_ERROR, msg=error)
            post_event(self._eventHandler, event)

        self.__close()

    def stop(self):
        self._cancel = True


class Timeout(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.name = 'GPS Timeout'

        self._callback = callback
        self._done = threading.Event()
        self._reset = True

        self.start()

    def run(self):
        while self._reset:
            self._reset = False
            self._done.wait(TIMEOUT)

        if not self._done.isSet():
            self._callback()

    def reset(self):
        self._reset = True
        self._done.clear()

    def cancel(self):
        self._done.set()


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
