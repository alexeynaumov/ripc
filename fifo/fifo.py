from PyQt4.QtCore import QObject, SIGNAL, QThread
from io import BaseFIFOReader, BaseFIFOWriter


class FIFOReader(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.__path = None

        class ReadingThread(QThread):
            def __init__(self, parent):
                QThread.__init__(self, parent)

            def run(self):
                parent = self.parent()
                reader = BaseFIFOReader()
                reader.path = parent.path
                reader.open()

                QObject.connect(self, SIGNAL("read"), parent._FIFOReader__onReadyRead)

                while True:
                    data = reader.read()
                    self.emit(SIGNAL("read"), data)

        self.__readingThread = ReadingThread(self)
        self.__on_read = None  # on-read callback

    def __del__(self):
        self.close()

    def __onReadyRead(self, data):
        if self.__on_read:
            self.__on_read(data)

    def open(self):
        self.__readingThread.start()

    def close(self):
        self.__readingThread.wait()
        self.__readingThread.quit()

    @property
    def isOpen(self):
        return self.__readingThread.isRunning()

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path):
        self.__path = path

    @property
    def onRead(self):
        return self.__on_read

    @onRead.setter
    def onRead(self, callback):
        self.__on_read = callback


class FIFOWriter(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)

        self.__baseFIFOWriter = BaseFIFOWriter()

    def open(self):
        self.__baseFIFOWriter.open()

    def close(self):
        self.__baseFIFOWriter.close()

    def write(self, data):
        self.__baseFIFOWriter.write(data)

    @property
    def isOpen(self):
        return self.__baseFIFOWriter.isOpen

    @property
    def path(self):
        return self.__baseFIFOWriter.path

    @path.setter
    def path(self, path):
        self.__baseFIFOWriter.path = path