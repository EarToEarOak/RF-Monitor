# RF Monitor #

Copyright 2015 Al Brown

al [at] eartoearoak.com

RF signal monitor for recording the time and location of signals which exceed a threshold. For use with a RTLSDR dongle.


## Requirements ##

- [Python 2.7](http://www.python.org) or greater
- [wxPython](http://www.wxpython.org/)


## Installation ##

`pip install rf-monitor`

## Usage ##

`rf_monitor.py [file]`

**Main Window**

Set the frequency, gain and calibration in the toolbar located at the bottom of the main window.

To add 'monitors' for frequencies of interest click the '+' button on the right hand side of the toolbar.

The 'Start' button begins radio reception and 'Stop' finishes it.

Press 'Record' to begin recording signals which exceed the threshold of each monitor. Press it again to stop recording.

**Monitors**

Each monitor allows you to watch a particular frequency and record when it's level exceeds a threshold.  The colour on the left corresponds to the plots in the spectrum and timeline views (see below).

Set the frequency using the drop-down list and set level threshold with the slider.
Each monitor can be enabled and an alert played if the respective check boxes are ticked.

To remove a monitor remove the tick from the 'Enabled' box and press the '-' button.

**Spectrum View**

This window (found in the View menu) displays the received frequency spectrum and marks the frequencies and thresholds of any monitors that are enabled.

To begin reception press the start button on the toolbar in the main window.

**Timeline View**
This window (found in the View menu) displays recorded signals for enabled monitors.

Blocks are displayed when the signal is larger than the threshold, lighter coloured blocks indicate the recording periods.


**Plot controls**

To zoom and pan the plots press the 'Pan' button in the plot's toolbar (crossed arrows).
Drag using the left mouse button to pan and use the right button to zoom in and out.

**GPS**

A NMEA serial GPS can be connected, this will record the location for each signal as it's recorded.

Set up the GPS by opening 'GPS Settings' in the edit menu, select the port and baud rate of your GPS and tick the enable box.

**Command Line Mode**

Once you have added your monitors and saved the file you can run the application from the command line.

Specify the file you want to use with the '-c' switch:

`python rfmonitor.py -c <savedfile.rfmon>`

The application will begin recording signals, press Ctrl-C to exit it.

To use GPS add the port using '-p' and the baud rate with '-b'

`python rfmonitor.py -p <serial port> -b <baud> -c <savedfile.rfmon>`

For example on Windows:

`python rfmonitor.py -p COM4 -b 115200 -c savedfile.rfmon`

or Linux

`python rfmonitor.py -p /dev/ttyUSB0 -b 115200 -c savedfile.rfmon`


**Network**

A TCP server is available on port 15622 which outputs JSON describing the recorded signals, for example:

`{"Frequency": 89000000, "Signal": {"Start": 1447075856.359, "End": 1447075856.632, "Level": -24.174076948140357}}`

## License ##

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
