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

import locale

from wx import xrc
from wx.lib import masked


class XrcHandlerNumCtrl(xrc.XmlResourceHandler):
    def CanHandle(self, node):
        return self.IsOfClass(node, 'NumCtrl')

    def DoCreateResource(self):
        integerWidth = int(self.GetParamValue('integerwidth')) if self.HasParam('integerwidth') else 4
        fractionWidth = int(self.GetParamValue('fractionwidth')) if self.HasParam('fractionwidth') else 3

        ctrl = masked.NumCtrl(
                self.GetParentAsWindow(),
                self.GetID(),
                allowNegative=False,
                integerWidth=integerWidth,
                fractionWidth=fractionWidth,
                groupChar=' ',
                allowNone=False,
                decimalChar=locale.localeconv()['decimal_point'])
        self.SetupWindow(ctrl)
        self.CreateChildren(ctrl)

        return ctrl


if __name__ == '__main__':
    exit(1)
    print 'Please run rfmonitor.py'
