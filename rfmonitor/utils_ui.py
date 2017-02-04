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

import pkg_resources
from wx import xrc
import wx


def get_resource(resource):
    if not hasattr(sys, 'frozen'):
        return pkg_resources.resource_filename('rfmonitor.ui', resource)
    else:
        return os.path.join(sys._MEIPASS, 'ui', resource)


def load_ui(resource):
    return xrc.XmlResource(get_resource(resource))


def load_sound(resource):
    return wx.Sound(get_resource(resource))


def load_bitmap(resource, size=None):
    bitmap = wx.Bitmap(get_resource(resource), wx.BITMAP_TYPE_PNG)
    if size is not None:
        image = wx.ImageFromBitmap(bitmap)
        image.Rescale(size.GetWidth(), size.GetHeight(),
                      wx.IMAGE_QUALITY_HIGH)
        bitmap = image.ConvertToBitmap()

    return bitmap


def load_icon(filename):
    icon = wx.EmptyIcon()
    bitmap = load_bitmap(filename)
    icon.CopyFromBitmap(bitmap)
    return icon


if __name__ == '__main__':
    print 'Please run rfmonitor.py'
    exit(1)
