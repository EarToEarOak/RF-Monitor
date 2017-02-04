#! /usr/bin/env python
#
#
# RF Monitor
#
#
# Copyright 2015 - 2017 Al Brown
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

from setuptools import setup, find_packages

from rfmonitor.version import VERSION


setup(name='rf-monitor',
      version='.'.join([str(x) for x in VERSION]),
      description='RF signal monitor',
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Communications :: Ham Radio',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Visualization'],
      keywords='wildlife tracking ecology',
      url='https://eartoearoak.com/software/rf-monitor',
      author='Al Brown',
      author_email='al [at] eartoearok.com',
      license='GPLv3',
      packages=find_packages(),
      package_data={'rfmonitor.ui': ['*']},
      scripts=['rf_monitor.py'],
      install_requires=['matplotlib', 'numpy', 'pyrtlsdr', 'pyserial'])
