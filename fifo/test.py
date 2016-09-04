import sys
import signal
from time import sleep
from PyQt4.QtCore import QCoreApplication, QThread
from fifo import FIFOReader, FIFOWriter

signal.signal(signal.SIGINT, signal.SIG_DFL)

def onRead(data):
    print("Rx: {}".format(data))

app = QCoreApplication(sys.argv)

try:
    reader = FIFOReader()
    reader.path = "/home/alex_newman/Projects/Sandbox/Python/ripc_001/fifo/fifo"
    reader.onRead = onRead
    reader.open()

    writer = FIFOWriter()
    writer.path = "/home/alex_newman/Projects/Sandbox/Python/ripc_001/fifo/fifo"
    writer.open()

except Exception as exception:
    print "Shit happened: %s" % exception
    reader.close()
    writer.close()

for idx in xrange(5):
    data = str(idx)*5
    writer.write(data)
    print("TX: {}".format(data))
    sleep(0.1)  # comment this line to test the hard way

sys.exit(app.exec_())