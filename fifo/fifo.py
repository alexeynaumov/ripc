from PyQt4.QtCore import QObject, SIGNAL, QThread
from io import BaseFIFOReader, BaseFIFOWriter


class FIFOReader(QObject):
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.__baseFIFOReader = BaseFIFOReader()

        class Worker(QObject):
            def __init__(self, reader):
                QObject.__init__(self)
                self.__reader = reader

            def read(self):
                while True:
                    data = self.__reader.read()
                    self.emit(SIGNAL("read"), data)

        self.__on_read = None  # on-read callback

        self.__thread = QThread(self)
        self.__worker = Worker(self.__baseFIFOReader)

        # READER AND WRITER LIVE IN THEIR OWN THREADS !!
        self.__worker.moveToThread(self.__thread)

        result = True
        # TOUCH READER ONLY WITH SIGNALS !!
        result &= QObject.connect(self.__worker, SIGNAL("read"), self.__onReadyRead)
        # START THE READING THREAD WITH THE SIGNAL TOO !!
        result &= QObject.connect(self.__thread, SIGNAL("started()"), self.__worker.read)

        if not result:
            raise RuntimeError("Error connecting signals to slots in FIFOReader.__init__")

    def __del__(self):
        self.__baseFIFOReader.close()
        self.__thread.wait()
        self.__thread.quit()

    def __onReadyRead(self, data):
        if self.__on_read:
            self.__on_read(data)

    def open(self):
        self.__baseFIFOReader.open()
        self.__thread.start()

    def close(self):
        self.__baseFIFOReader.close()

    @property
    def isOpen(self):
        return self.__baseFIFOReader.isOpen

    @property
    def path(self):
        return self.__baseFIFOReader.path

    @path.setter
    def path(self, path):
        self.__baseFIFOReader.path = path

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

        class Worker(QObject):
            def __init__(self, writer):
                QObject.__init__(self)
                self.__writer = writer
                self.__dataToWrite = ""

            def write(self, data):
                self.__dataToWrite += data

                while self.__dataToWrite:
                    char = self.__dataToWrite[0]

                    self.__dataToWrite = self.__dataToWrite[1:]

                    self.__writer.write(char)

        self.__thread = QThread(self)
        self.__worker = Worker(self.__baseFIFOWriter)

        # READER AND WRITER LIVE IN THEIR OWN THREADS !!
        self.__worker.moveToThread(self.__thread)

        result = True
        # TOUCH WRITER ONLY WITH SIGNALS !!
        result &= QObject.connect(self, SIGNAL("write"), self.__worker.write)

        if not result:
            raise RuntimeError("Error connecting signals to slots in FIFOWriter.__init__")

    def __del__(self):
        self.__baseFIFOWriter.close()
        self.__thread.wait()
        self.__thread.quit()

    def open(self):
        self.__baseFIFOWriter.open()
        self.__thread.start()

    def close(self):
        self.__baseFIFOWriter.close()

    def write(self, data):
        self.emit(SIGNAL("write"), data)

    @property
    def isOpen(self):
        return self.__baseFIFOWriter.isOpen

    @property
    def path(self):
        return self.__baseFIFOWriter.path

    @path.setter
    def path(self, path):
        self.__baseFIFOWriter.path = path