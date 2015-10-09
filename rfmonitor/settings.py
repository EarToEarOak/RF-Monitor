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


class Settings(object):
    class Monitor(object):
        enabled = False
        freq = 0
        threshold = 0
        signals = []

    def __init__(self):
        self._config = wx.Config('rf-monitor')

        self._freq = 118.0
        self._gain = 0
        self._monitors = []

        self.__load()

    def __load(self):
        self._config.SetPath('/')
        self._freq = self._config.ReadFloat('frequency', self._freq)
        self._gain = self._config.ReadFloat('gain', self._gain)

        self._config.SetPath('/Monitors')
        group = self._config.GetFirstGroup()
        while group[0]:
            self._config.SetPath('/Monitors/' + group[1])
            monitor = Settings.Monitor()
            monitor.enabled = self._config.ReadBool('enabled', 0)
            monitor.freq = self._config.ReadInt('frequency', 0) / 1e6
            monitor.threshold = self._config.ReadFloat('threshold', 0)
            self._monitors.append(monitor)
            self._config.SetPath("/Monitors")
            group = self._config.GetNextGroup(group[2])

    def set_freq(self, freq):
        self._freq = freq

    def get_freq(self):
        return self._freq

    def set_gain(self, gain):
        self._gain = gain

    def get_gain(self):
        return self._gain

    def clear_monitors(self):
        self._monitors = []
        self._config.DeleteGroup('/Monitors')

    def add_monitor(self, enabled, freq, threshold):
        monitor = Settings.Monitor()
        monitor.enabled = enabled
        monitor.freq = freq
        monitor.threshold = threshold
        self._monitors.append(monitor)

    def get_monitors(self):
        return self._monitors

    def save(self):
        self._config.SetPath('/')
        self._config.WriteFloat('frequency', self._freq)
        self._config.WriteFloat('gain', self._gain)

        for i in range(len(self._monitors)):
            self._config.SetPath('/Monitors/' + str(i))
            self._config.WriteBool('enabled', self._monitors[i].enabled)
            self._config.WriteInt('frequency', self._monitors[i].freq * 1e6)
            self._config.WriteFloat('threshold', self._monitors[i].threshold)


if __name__ == '__main__':
    exit(1)
    print 'Please run rfmonitor.py'
