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

import ctypes
import threading
import time

from matplotlib.mlab import psd
import numpy
import rtlsdr

from rfmonitor.constants import SAMPLE_RATE, SAMPLES, BINS
from rfmonitor.events import Event, Events, post_event


class Receive(threading.Thread):
    def __init__(self, eventHandler, freq, gain, cal):
        threading.Thread.__init__(self)
        self.name = 'Receive'
        self.daemon = True

        self._cancel = False
        self._freq = freq
        self._gain = gain
        self._cal = cal
        self._eventHandler = eventHandler
        self._sdr = None
        self._capture = (ctypes.c_ubyte * SAMPLES)()

        devices = rtlsdr.librtlsdr.rtlsdr_get_device_count()
        if devices == 0:
            event = Event(Events.SCAN_ERROR, msg='No device found')
            post_event(eventHandler, event)
        else:
            self.start()

    def __capture(self, data, _sdr):
        timestamp = time.time()
        dst = ctypes.byref(self._capture, 0)
        ctypes.memmove(dst, data, len(data))

        iq = self.__stream_to_complex(self._capture)
        l, f = psd(iq, BINS, SAMPLE_RATE,
                   scale_by_freq=False,
                   noverlap=-SAMPLES / 64)
        f /= 1e6
        f += self._freq

        event = Event(Events.SCAN_DATA, timestamp=timestamp, l=l, f=f)
        post_event(self._eventHandler, event)

    def __stream_to_complex(self, stream):
        bytes_np = numpy.ctypeslib.as_array(stream)
        iq = bytes_np.astype(numpy.float32).view(numpy.complex64)
        iq /= 255 / 2
        iq -= 1 + 1j

        return iq

    def set_frequency(self, frequency):
        self._freq = frequency
        self._sdr.set_center_freq(self._freq * 1e6)

    def run(self):
        self._sdr = rtlsdr.RtlSdr()
        self._sdr.set_sample_rate(SAMPLE_RATE)
        self.set_frequency(self._freq)
        cal = self._sdr.get_freq_correction()
        if self._cal != cal:
            self._sdr.set_freq_correction(self._cal)
        self._sdr.set_gain(self._gain)
        time.sleep(1)

        self._sdr.read_bytes_async(self.__capture, SAMPLES)

    def stop(self):
        self._cancel = True
        if self._sdr is not None:
            try:
                self._sdr.cancel_read_async()
            except IOError:
                pass
            finally:
                self._sdr.close()


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
