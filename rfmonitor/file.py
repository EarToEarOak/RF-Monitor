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

from collections import OrderedDict
import json

from rfmonitor.constants import APP_NAME
from rfmonitor.monitor import Monitor, Period
from rfmonitor.signals import Signal


VERSION = 1


def save_recordings(filename, freq, gain, monitors):

    jsonMonitors = []
    for monitor in monitors:
        jsonMonitor = OrderedDict()
        jsonMonitor['Enabled'] = monitor.get_enabled()
        jsonMonitor['Alert'] = monitor.get_alert()
        jsonMonitor['Frequency'] = int(monitor.get_frequency() * 1e6)
        jsonMonitor['Threshold'] = monitor.get_threshold()
        jsonMonitor['Signals'] = [signal.to_list()
                                  for signal in monitor.get_signals()]
        jsonMonitor['Periods'] = [period.to_list()
                                  for period in monitor.get_periods()]
        jsonMonitors.append(jsonMonitor)

    fileData = OrderedDict()
    fileData['Version'] = VERSION
    fileData['Frequency'] = freq * 1e6
    fileData['Gain'] = gain
    fileData['Monitors'] = jsonMonitors

    data = [APP_NAME, fileData]

    handle = open(filename, 'wb')
    handle.write(json.dumps(data, indent=4))
    handle.close()


def load_recordings(filename):
    handle = open(filename, 'rb')
    data = json.loads(handle.read())
    handle.close()

    _header = data[0]
    _version = data[1]['Version']
    freq = data[1]['Frequency'] / 1e6
    gain = data[1]['Gain'] if 'Gain' in data[1] else None
    jsonMonitors = data[1]['Monitors']

    monitors = []
    for jsonMonitor in jsonMonitors:
        alert = jsonMonitor['Alert'] if 'Alert' in jsonMonitor else False
        signals = [Signal().from_list(signal)
                   for signal in jsonMonitor['Signals']]
        periods = []
        if 'Periods' in jsonMonitor:
            periods = [Period().from_list(period)
                       for period in jsonMonitor['Periods']]
        monitor = Monitor(jsonMonitor['Enabled'],
                          alert,
                          jsonMonitor['Frequency'] / 1e6,
                          jsonMonitor['Threshold'],
                          signals,
                          periods)
        monitors.append(monitor)

    return freq, gain, monitors


def format_recording(freq, recording):
    record = OrderedDict()
    record['Start'] = recording.start
    record['End'] = recording.end
    record['Level'] = recording.level
    if recording.location is not None:
        record['location'] = recording.location

    signal = OrderedDict()
    signal['Frequency'] = int(freq * 1e6)
    signal['Signal'] = record

    return json.dumps(signal)


if __name__ == '__main__':
    exit(1)
    print 'Please run rfmonitor.py'
