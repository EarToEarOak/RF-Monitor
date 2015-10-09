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

from matplotlib.mlab import psd
import numpy
from rtlsdr.rtlsdr import RtlSdr
from wx import xrc
import wx

from constants import BINS, SAMPLE_RATE, LEVEL_MIN
from dialog_about import DialogAbout
from dialog_spectrum import DialogSpectrum, EVT_SPECTRUM_CLOSE
from file import save_recordings, load_recordings
from panel_monitor import PanelMonitor
from panel_toolbar import XrcHandlerToolbar
from receive import Receive, EVT_SCAN_ERROR, EVT_SCAN_DATA
from settings import Settings
from ui import load_ui


class RfMonitor(wx.App):
    def __init__(self):
        try:
            wx.Dialog.EnableLayoutAdaptation(True)
        except AttributeError:
            pass
        wx.App.__init__(self, redirect=False)


class FrameMain(wx.Frame):
    def __init__(self, title):
        self._monitors = []
        self._freqs = []
        self._levels = numpy.zeros(BINS, dtype=numpy.float32)
        self._settings = Settings()
        self._filename = None
        self._receive = None
        self._dialogSpectrum = None

        self._ui = load_ui('FrameMain.xrc')

        handlerToolbar = XrcHandlerToolbar()
        self._ui.AddHandler(handlerToolbar)

        self._frame = self._ui.LoadFrame(None, 'FrameMain')
        self._frame.SetTitle(title)

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
        idSpectrum = xrc.XRCID('menuSpectrum')
        self._frame.Bind(wx.EVT_MENU, self.__on_spectrum, id=idSpectrum)
        self._menuSpectrum = self._menu.FindItemById(idSpectrum)
        idClose = xrc.XRCID('menuClose')
        self._menuClose = self._menu.FindItemById(idClose)
        self._frame.Bind(wx.EVT_MENU, self.__on_exit, id=idClose)
        idAbout = xrc.XRCID('menuAbout')
        self._frame.Bind(wx.EVT_MENU, self.__on_about, id=idAbout)

        self._frame.Bind(EVT_SPECTRUM_CLOSE, self.__on_spectrum_close)
        self._frame.Bind(EVT_SCAN_ERROR, self.__on_scan_error)
        self._frame.Bind(EVT_SCAN_DATA, self.__on_scan_data)

        self._frame.Bind(wx.EVT_CLOSE, self.__on_exit)

        self._frame.Show()

    def __add_monitors(self):
        for monitor in self._settings.get_monitors():
            panelMonitor = PanelMonitor(self._window)
            panelMonitor.set_callback(self.__on_del)
            panelMonitor.set_freqs(self._freqs)
            panelMonitor.set_enabled(monitor.enabled)
            panelMonitor.set_freq(monitor.freq)
            panelMonitor.set_threshold(monitor.threshold)
            self.__add_monitor(panelMonitor)

        if not len(self._monitors):
            panelMonitor = PanelMonitor(self._window)
            panelMonitor.set_callback(self.__on_del)
            panelMonitor.set_freqs(self._freqs)
            self.__add_monitor(panelMonitor)

        self._frame.Layout()

    def __add_monitor(self, monitor):
        self._monitors.append(monitor)
        self._sizerWindow.Add(monitor, 0, wx.ALL | wx.EXPAND, 5)

    def __clear_monitors(self):
        for _i in range(len(self._monitors)):
            self._sizerWindow.Hide(0)
            self._sizerWindow.Remove(0)

        self._frame.Layout()

        self._monitors = []

    def __is_saved(self):
        for monitor in self._monitors:
            if not monitor.get_saved():
                return False

        return True

    def __on_freq(self, freq):
        for _i in range(len(self._monitors)):
            self._sizerWindow.Hide(0)
            self._sizerWindow.Remove(0)
        self._frame.Layout()

        del self._monitors[:]

        _l, freqs = psd(numpy.zeros(2, dtype=numpy.complex64),
                        BINS, SAMPLE_RATE)
        freqs /= 1e6
        freqs += freq
        self._freqs = freqs.tolist()

    def __on_start(self):
        if not self.__save_warning():
                return

        self._menuOpen.Enable(False)
        self._menuSave.Enable(False)
        self._menuSaveAs.Enable(False)
        self._menuClear.Enable(False)
        self._menuClose.Enable(False)
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
        self._menuOpen.Enable(True)
        self._menuSave.Enable(True)
        self._menuSaveAs.Enable(True)
        self._menuClear.Enable(True)
        self._menuClose.Enable(True)
        if self._receive is not None:
            self._receive.stop()
            self._receive = None
        for monitor in self._monitors:
            monitor.set_level(LEVEL_MIN, 0)
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

    def __on_open(self, _event):
        if not self.__save_warning():
                return

        dlg = wx.FileDialog(self._frame,
                            'Open File', '', '',
                            'rfmon files (*.rfmon)|*.rfmon',
                            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_CANCEL:
            return

        load_recordings(dlg.GetPath(),
                        self._settings)

        self._toolbar.set_freq(self._settings.get_freq())
        self.__clear_monitors()
        self.__add_monitors()

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

        self.__update_settings()
        self._settings.save()

        self._frame.Destroy()

    def __on_scan_error(self, event):
        wx.MessageBox(event.msg,
                      'Error', wx.OK | wx.ICON_ERROR)
        self._toolbar.enable_start(True)

    def __on_scan_data(self, event):
        levels = numpy.log10(event.l)
        levels *= 10

        self._levels += levels
        self._levels /= 2.

        for monitor in self._monitors:
            freq = monitor.get_freq()
            if monitor.is_enabled() and freq in self._freqs:
                index = numpy.where(freq == event.f)[0]
                monitor.set_level(levels[index], event.timestamp)

        if self._dialogSpectrum is not None:
            self._dialogSpectrum.set_spectrum(self._freqs,
                                              self._levels,
                                              event.timestamp)

    def __update_settings(self):
        self._settings.set_freq(self._toolbar.get_freq())
        self._settings.set_gain(self._toolbar.get_gain())
        self._settings.clear_monitors()
        for monitor in self._monitors:
            self._settings.add_monitor(monitor.is_enabled(),
                                       monitor.get_freq(),
                                       monitor.get_threshold())

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

        save_recordings(self._filename,
                        self._settings)

    def __save_warning(self):
        if not self.__is_saved():
            resp = wx.MessageBox('Data is not saved, quit?', 'Warning',
                                 wx.OK | wx.CANCEL | wx.ICON_WARNING)
            if resp != wx.OK:
                return False

        return True


if __name__ == '__main__':
    exit(1)
    print 'Please run rfmonitor.py'
