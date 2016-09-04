# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 Alexey Naumov <rocketbuzzz@gmail.com>
#
# This file is part of ripc.
#
# rserial is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import array
import os
import select
import termios
import fcntl


class FIFOError(Exception):
    pass


class BaseFIFO(object):
    def __init__(self):
        self.__fd = None
        self.__path = None
        self.__isOpen = False

    def __del__(self):
        self.close()

    def __isOpen(self):
        return self.__isOpen

    def open(self):
        if None == self.path:
            raise FIFOError("FIFO path not set")

        self.__fd = os.open(self.__path, os.O_NONBLOCK|os.O_RDWR)
        if -1 == self.__fd:
            self.__isOpen = False
            raise FIFOError("Error opening FIFO: %s" % self.__path)

        self.__isOpen = True

    def close(self):
        if self.__path:
            self.__path = None

    @property
    def isOpen(self):
        return self.__isOpen

    @property
    def fd(self):
        return self.__fd

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path):
        if self.isOpen:
            raise FIFOError("Cannot change FIFO path while reading")

        self.__path = path


class ReadMixin(object):
    def read(self):
        try:
            ready, _, _ = select.select([self.fd], [], [])
        except select.error as error:
            raise FIFOError("Error reading data from FIFO %s: %s" % (self.path, error.message))

        if not ready:
            raise FIFOError("Error reading data from FIFO %s: " % self.path)

        buffer = array.array('i', [0])
        if -1 == fcntl.ioctl(self.fd, termios.FIONREAD, buffer, 1):
            raise FIFOError("Error getting number of bytes available for reading")

        bytesAvailable = buffer[0]

        try:
            data = os.read(self.fd, bytesAvailable)
        except OSError as error:
            raise FIFOError("Error reading data from FIFO %s: %s" % (self.path, error.message))

        return data


class WriteMixin(object):
    def write(self, data):
        if not self.isOpen:
            raise FIFOError("FIFO not open")

        bytesToWrite = length = len(data)

        while bytesToWrite > 0:
            try:
                bytesWritten = os.write(self.fd, data)
            except OSError as error:
                raise FIFOError('Error writing data to FIFO %s: %s' % (self.path, error.strerror))

            try:
                _, ready, _ = select.select([], [self.fd], [])
            except select.error as error:
                raise FIFOError("Error writing data to FIFO %s: %s" % (self.path, error.message))

            if not ready:
                raise FIFOError("Error writing data to FIFO %s" % self.path)

            data = data[bytesWritten:]
            bytesToWrite -= bytesWritten

        return length


class BaseFIFOReader(ReadMixin, BaseFIFO):
    def __init__(self):
        BaseFIFO.__init__(self)

class BaseFIFOWriter(WriteMixin, BaseFIFO):
    def __init__(self):
        BaseFIFO.__init__(self)