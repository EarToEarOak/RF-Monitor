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

import wx

from rfmonitor.gps import GpsDevice


class Settings(object):
    def __init__(self):
        self._config = wx.Config('rf-monitor')

        self._freq = 118.0
        self._gain = 0
        self._cal = 0
        self._gps = GpsDevice()
        self._pushEnable = True
        self._pushUri = 'http://localhost/rfmonitor'

        self.__load()

    def __load(self):
        self._config.SetPath('/')
        self._freq = self._config.ReadFloat('frequency', self._freq)
        self._gain = self._config.ReadFloat('gain', self._gain)
        self._cal = self._config.ReadInt('calibration', self._cal)

        self._config.SetPath('/Gps')
        self._gps.enabled = self._config.ReadBool('enabled', self._gps.enabled)
        self._gps.port = self._config.Read('port', self._gps.port)
        self._gps.baud = self._config.ReadInt('baud', self._gps.baud)
        self._gps.bits = self._config.ReadInt('bits', self._gps.bits)
        self._gps.parity = self._config.Read('parity', self._gps.parity)
        self._gps.stops = self._config.ReadInt('stops', self._gps.stops)
        self._gps.soft = self._config.ReadBool('soft', self._gps.soft)

        self._config.SetPath('/Push')
        self._pushEnable = self._config.ReadBool('pushEnable', self._pushEnable)
        self._pushUri = self._config.Read('pushUri', self._pushUri)

    def set_freq(self, freq):
        self._freq = freq

    def set_gain(self, gain):
        self._gain = gain

    def set_cal(self, cal):
        self._cal = cal

    def set_push_enable(self, enable):
        self._pushEnable = enable

    def set_push_uri(self, uri):
        self._pushUri = uri

    def get_freq(self):
        return self._freq

    def get_gain(self):
        return self._gain

    def get_cal(self):
        return self._cal

    def get_gps(self):
        return self._gps

    def get_push_enable(self):
        return self._pushEnable

    def get_push_uri(self):
        return self._pushUri

    def save(self):
        self._config.SetPath('/')
        self._config.WriteFloat('frequency', self._freq)
        self._config.WriteFloat('gain', self._gain)
        self._config.WriteInt('calibration', self._cal)

        self._config.SetPath('/Gps')
        self._config.WriteBool('enabled', self._gps.enabled)
        self._config.Write('port', self._gps.port)
        self._config.WriteInt('baud', self._gps.baud)
        self._config.WriteInt('bits', self._gps.bits)
        self._config.Write('parity', self._gps.parity)
        self._config.WriteInt('stops', self._gps.stops)
        self._config.WriteBool('soft', self._gps.soft)

        self._config.SetPath('/Push')
        self._config.WriteBool('pushEnable', self._pushEnable)
        self._config.Write('pushUri', self._pushUri)


if __name__ == '__main__':
    exit(1)
    print 'Please run rfmonitor.py'
