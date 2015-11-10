#
# rtlsdr_scan
#
# http://eartoearoak.com/software/rtlsdr-scanner
#
# Copyright 2012, 2015 Al Brown
#
# A frequency scanning GUI for the OsmoSDR rtl-sdr library at
# http://sdr.osmocom.org/trac/wiki/rtl-sdr
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

import platform

from git import Repo
from git.exc import GitCommandError
from PyInstaller.utils.win32 import versioninfo
from PyInstaller import compat
import sys


def create_version():
    repo = Repo()
    if repo.is_dirty():
        sys.stderr.write('Repo is dirty, exiting')
        exit(1)

    try:
        version = repo.git.describe()
    except GitCommandError:
        version = repo.rev_parse(rev='HEAD')
        version = repo.git.rev_parse(version, short=4)

    return version


def build(version):
    system = platform.system().lower()
    architecture, _null = platform.architecture()
    filename = 'rfmonitor-' + version + '-' + system + '-' + architecture.lower()

    excludes = ['pyside', 'qt', 'scipy']
    a = Analysis(['rfmonitor.py'],
                excludes=excludes)

    a.datas += Tree('rfmonitor/ui', prefix='ui')

    pyz = PYZ(a.pure)

    exe = EXE(pyz,
              a.scripts + [('O', '', 'OPTION')],
              a.binaries,
              a.zipfiles,
              a.datas,
              name=os.path.join('dist', filename),
              icon='logo.ico',
              upx=True)


version = create_version()
build(version)
