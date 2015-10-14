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

import os
import sys

from matplotlib.mlab import psd
import numpy
from rtlsdr.rtlsdr import RtlSdr
from wx import xrc
import wx

from rfmonitor.constants import BINS, SAMPLE_RATE, LEVEL_MIN, APP_NAME, \
    GPS_RETRY
from rfmonitor.dialog_about import DialogAbout
from rfmonitor.dialog_gps import DialogGps
from rfmonitor.dialog_spectrum import DialogSpectrum, EVT_SPECTRUM_CLOSE
from rfmonitor.dialog_timeline import DialogTimeline, EVT_TIMELINE_CLOSE
from rfmonitor.events import EVENT_THREAD, Events
from rfmonitor.file import save_recordings, load_recordings, format_recording
from rfmonitor.gps import Gps
from rfmonitor.panel_monitor import PanelMonitor
from rfmonitor.panel_toolbar import XrcHandlerToolbar
from rfmonitor.receive import Receive
from rfmonitor.server import Server
from rfmonitor.settings import Settings
from rfmonitor.ui import load_ui


class RfMonitor(wx.App):
    def __init__(self):
        try:
            wx.Dialog.EnableLayoutAdaptation(True)
        except AttributeError:
            pass
        wx.App.__init__(self, redirect=False)


class FrameMain(wx.Frame):
    def __init__(self):
        self._monitors = []
        self._freqs = []
        self._levels = numpy.zeros(BINS, dtype=numpy.float32)
        self._settings = Settings()
        self._filename = None
        self._receive = None
        self._dialogTimeline = None
        self._dialogSpectrum = None
        self._gps = None
        self._location = None

        self._ui = load_ui('FrameMain.xrc')

        handlerToolbar = XrcHandlerToolbar()
        self._ui.AddHandler(handlerToolbar)

        self._frame = self._ui.LoadFrame(None, 'FrameMain')
        self.__set_title()

        self._window = xrc.XRCCTRL(self._frame, 'window')
        self._status = xrc.XRCCTRL(self._frame, 'statusBar')
        self._toolbar = xrc.XRCCTRL(self._frame, 'PanelToolbar')

        self._sizerWindow = self._window.GetSizer()

        sdr = RtlSdr()
        gains = sdr.get_gains()
        gains = [float(gain) / 10. for gain in gains]
        sdr.close()

        self._toolbar.set_callbacks(self.__on_freq,
                                    self.__on_start,
                                    self.__on_rec,
                                    self.__on_stop,
                                    self.__on_add)
        self._toolbar.enable_start(True)
        self._toolbar.set_freq(self._settings.get_freq())
        self._toolbar.set_gains(gains)
        self._toolbar.set_gain(self._settings.get_gain())

        self.__add_monitors()

        self._server = Server(self._frame)

        self.__start_gps()

        self._menu = self._frame.GetMenuBar()

        idOpen = xrc.XRCID('menuOpen')
        self._menuOpen = self._menu.FindItemById(idOpen)
        self._frame.Bind(wx.EVT_MENU, self.__on_open, id=idOpen)
        idSave = xrc.XRCID('menuSave')
        self._menuSave = self._menu.FindItemById(idSave)
        self._frame.Bind(wx.EVT_MENU, self.__on_save, id=idSave)
        idSaveAs = xrc.XRCID('menuSaveAs')
        self._menuSaveAs = self._menu.FindItemById(idSaveAs)
        self._frame.Bind(wx.EVT_MENU, self.__on_save_as, id=idSaveAs)
        idClear = xrc.XRCID('menuClear')
        self._menuClear = self._menu.FindItemById(idClear)
        self._frame.Bind(wx.EVT_MENU, self.__on_clear, id=idClear)
        idGps = xrc.XRCID('menuGps')
        self._menuGps = self._menu.FindItemById(idGps)
        self._frame.Bind(wx.EVT_MENU, self.__on_gps, id=idGps)
        idTimeline = xrc.XRCID('menuTimeline')
        self._frame.Bind(wx.EVT_MENU, self.__on_timeline, id=idTimeline)
        self._menuTimeline = self._menu.FindItemById(idTimeline)
        idSpectrum = xrc.XRCID('menuSpectrum')
        self._frame.Bind(wx.EVT_MENU, self.__on_spectrum, id=idSpectrum)
        self._menuSpectrum = self._menu.FindItemById(idSpectrum)
        idExit = xrc.XRCID('menuExit')
        self._menuExit = self._menu.FindItemById(idExit)
        self._frame.Bind(wx.EVT_MENU, self.__on_exit, id=idExit)
        idAbout = xrc.XRCID('menuAbout')
        self._frame.Bind(wx.EVT_MENU, self.__on_about, id=idAbout)

        self._frame.Bind(EVT_TIMELINE_CLOSE, self.__on_timeline_close)
        self._frame.Bind(EVT_SPECTRUM_CLOSE, self.__on_spectrum_close)

        self._frame.Bind(wx.EVT_CLOSE, self.__on_exit)

        self._frame.Connect(-1, -1, EVENT_THREAD, self.__on_event)

        self._frame.Show()

    def __on_freq(self, freq):
        _l, freqs = psd(numpy.zeros(2, dtype=numpy.complex64),
                        BINS, SAMPLE_RATE)
        freqs /= 1e6
        freqs += freq
        self._freqs = freqs.tolist()

    def __on_start(self):
        self.__enable_controls(False)
        if self._receive is None:
            self._receive = Receive(self._frame,
                                    self._toolbar.get_freq(),
                                    self._toolbar.get_gain())

    def __on_rec(self, recording):
        if recording:
            self.__on_start()

        for monitor in self._monitors:
            monitor.set_recording(recording)

    def __on_stop(self):
        self.__enable_controls(True)
        if self._receive is not None:
            self._receive.stop()
            self._receive = None
        for monitor in self._monitors:
            monitor.set_level(LEVEL_MIN, 0, None)
        if self._dialogSpectrum is not None:
            self._dialogSpectrum.clear_spectrum()

    def __on_add(self):
        monitor = PanelMonitor(self._window)
        monitor.set_callback(self.__on_del)
        monitor.set_freqs(self._freqs)
        self.__add_monitor(monitor)

        self._frame.Layout()

    def __on_del(self, monitor):
        index = self._monitors.index(monitor)
        self._sizerWindow.Hide(index)
        self._sizerWindow.Remove(index)
        self._frame.Layout()

        self._monitors.remove(monitor)

        self._toolbar.enable_freq(not len(self._monitors))

    def __on_open(self, _event):
        if not self.__save_warning():
            return

        defDir, defFile = '', ''
        if self._filename is not None:
            defDir, defFile = os.path.split(self._filename)
        dlg = wx.FileDialog(self._frame,
                            'Open File',
                            defDir, defFile,
                            'rfmon files (*.rfmon)|*.rfmon',
                            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_CANCEL:
            return

        self.open(dlg.GetPath())

    def __on_save(self, _event):
        self.__save(False)

    def __on_save_as(self, _event):
        self.__save(True)

    def __on_clear(self, _event):
        resp = wx.MessageBox('Clear recorded data?', 'Warning',
                             wx.OK | wx.CANCEL | wx.ICON_WARNING)
        if resp != wx.OK:
            return

        for monitor in self._monitors:
            monitor.clear_signals()

    def __on_gps(self, _event):
        dlg = DialogGps(self._frame, self._settings.get_gps())
        if dlg.ShowModal() == wx.ID_OK:
            self.__stop_gps()
            self.__start_gps()

    def __on_timeline(self, event):
        if event.IsChecked() and self._dialogTimeline is None:
            self._dialogTimeline = DialogTimeline(self._frame)
            self._dialogTimeline.set_signals(self.__get_signals())
            self._dialogTimeline.Show()
        elif self._dialogTimeline is not None:
            self._dialogTimeline.Destroy()
            self._dialogTimeline = None

    def __on_timeline_close(self, _event):
        self._menuTimeline.Check(False)
        self._dialogTimeline = None

    def __on_spectrum(self, event):
        if event.IsChecked() and self._dialogSpectrum is None:
            self._dialogSpectrum = DialogSpectrum(self._frame)
            self._dialogSpectrum.Show()
        elif self._dialogSpectrum is not None:
            self._dialogSpectrum.Destroy()
            self._dialogSpectrum = None

    def __on_spectrum_close(self, _event):
        self._menuSpectrum.Check(False)
        self._dialogSpectrum = None

    def __on_about(self, _event):
        dlg = DialogAbout(self._frame)
        dlg.ShowModal()

    def __on_exit(self, _event):
        if not self.__save_warning():
            return

        self.__on_stop()

        if self._server is not None:
            self._server.stop()

        self.__stop_gps()

        self.__update_settings()
        self._settings.save()

        self._frame.Destroy()

    def __on_event(self, event):
        if event.type == Events.SCAN_ERROR:
            self.__on_scan_error(event.data)

        elif event.type == Events.SCAN_DATA:
            self.__on_scan_data(event.data)
        elif event.type == Events.SERVER_ERROR:
            self.__on_server_error(event.data)
        elif event.type == Events.GPS_ERROR:
            self._status.SetStatusText(event.data['msg'], 1)
            self.__restart_gps()
        elif event.type == Events.GPS_WARN:
            self._status.SetStatusText(event.data['msg'], 1)
        elif event.type == Events.GPS_TIMEOUT:
            self._status.SetStatusText(event.data['msg'], 1)
            self.__restart_gps()
        elif event.type == Events.GPS_LOC:
            self._location = event.data['loc']
            loc = '{:9.5f}, {:9.5f}'.format(*self._location)
            self._status.SetStatusText(loc, 1)

    def __on_scan_error(self, event):
        wx.MessageBox(event['msg'],
                      'Error', wx.OK | wx.ICON_ERROR)
        self._toolbar.enable_start(True)

    def __on_scan_data(self, event):
        levels = numpy.log10(event['l'])
        levels *= 10

        self._levels += levels
        self._levels /= 2.

        updated = False
        for monitor in self._monitors:
            freq = monitor.get_freq()
            if monitor.is_enabled():
                index = numpy.where(freq == event['f'])[0]
                update = monitor.set_level(levels[index][0],
                                           event['timestamp'],
                                           self._location)
                if update:
                    updated = True
                    if self._server is not None:
                        recording = format_recording(freq, update)
                        self._server.send(recording)

        if self._dialogTimeline is not None and updated:
            self._dialogTimeline.set_signals(self.__get_signals())

        if self._dialogSpectrum is not None:
            self._dialogSpectrum.set_spectrum(self._freqs,
                                              self._levels,
                                              event['timestamp'])

    def __on_server_error(self, event):
        sys.stderr.write(event['msg'])
        self._server = None

    def __set_title(self):
        title = APP_NAME
        if self._filename is not None:
            _head, tail = os.path.split(self._filename)
            title += ' - ' + tail
        self._frame.SetTitle(title)

    def __update_settings(self):
        self._settings.set_freq(self._toolbar.get_freq())
        self._settings.set_gain(self._toolbar.get_gain())
        self._settings.clear_monitors()
        for monitor in self._monitors:
            self._settings.add_monitor(monitor.is_enabled(),
                                       monitor.get_freq(),
                                       monitor.get_threshold(),
                                       monitor.get_signals())

    def __save(self, prompt):
        if prompt or self._filename is None:
            defDir, defFile = '', ''
            if self._filename is not None:
                defDir, defFile = os.path.split(self._filename)
            dlg = wx.FileDialog(self._frame,
                                'Save File',
                                defDir, defFile,
                                'rfmon files (*.rfmon)|*.rfmon',
                                wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            self._filename = dlg.GetPath()

        self.__update_settings()
        save_recordings(self._filename,
                        self._settings)
        self.__set_title()

        for monitor in self._monitors:
            monitor.set_saved()

    def __save_warning(self):
        if not self.__is_saved():
            resp = wx.MessageBox('Data is not saved, continue?', 'Warning',
                                 wx.OK | wx.CANCEL | wx.ICON_WARNING)
            if resp != wx.OK:
                return False

        return True

    def open(self, filename):
        load_recordings(filename,
                        self._settings)

        self._filename = filename
        self.__set_title()
        self._toolbar.set_freq(self._settings.get_freq())
        self.__clear_monitors()
        self.__add_monitors()

        if self._dialogTimeline is not None:
            self._dialogTimeline.set_signals(self.__get_signals())

    def __enable_controls(self, enable):
        isSaved = self.__is_saved()

        self._menuOpen.Enable(enable)
        self._menuSave.Enable(enable)
        self._menuSaveAs.Enable(enable)
        self._menuClear.Enable(enable and isSaved)
        self._menuGps.Enable(enable)
        self._menuExit.Enable(enable)

    def __add_monitors(self):
        for monitor in self._settings.get_monitors():
            panelMonitor = PanelMonitor(self._window)
            panelMonitor.set_callback(self.__on_del)
            panelMonitor.set_freqs(self._freqs)
            panelMonitor.set_enabled(monitor.enabled)
            panelMonitor.set_freq(monitor.freq)
            panelMonitor.set_threshold(monitor.threshold)
            panelMonitor.set_signals(monitor.signals)
            self.__add_monitor(panelMonitor)

        self._frame.Layout()

    def __add_monitor(self, monitor):
        self._toolbar.enable_freq(False)

        self._monitors.append(monitor)
        self._sizerWindow.Add(monitor, 0, wx.ALL | wx.EXPAND, 5)

    def __clear_monitors(self):
        for _i in range(len(self._monitors)):
            self._sizerWindow.Hide(0)
            self._sizerWindow.Remove(0)

        self._frame.Layout()

        self._monitors = []
        self._toolbar.enable_freq(True)

    def __get_signals(self):
        return [(monitor.get_freq(),
                 monitor.get_signals())
                for monitor in self._monitors]

    def __is_saved(self):
        for monitor in self._monitors:
            if not monitor.get_saved():
                return False

        return True

    def __start_gps(self):
        if self._gps is None and self._settings.get_gps().enabled:
            self._status.SetStatusText('Staring GPS...', 1)
            self._gps = Gps(self._frame, self._settings.get_gps())

    def __stop_gps(self):
        if self._gps is not None:
            self._gps.stop()
            self._gps = None

    def __restart_gps(self):
        self.__stop_gps()
        wx.CallLater(GPS_RETRY * 1000, self.__start_gps)


if __name__ == '__main__':
    exit(1)
    print 'Please run rfmonitor.py'
