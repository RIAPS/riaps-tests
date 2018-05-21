from riaps.run.comp import Component
import logging
import os

class B(Component):
    def __init__(self):
        super(B, self).__init__()

        self.logpath = '/tmp/B.log'
        self.logFile = open(self.logpath, 'w')
        self.logFile.write('Actor B started\n')

        self.messageCounter = 0

    def on_subPort(self):
        msg = self.subPort.recv_pyobj()
        self.logFile.write("Subscribe: %s\n" % msg)

        msg = self.messageCounter
        self.messageCounter += 1

        self.pubPort.send_pyobj(msg)
        self.logFile.write("Publish: %s\n" % msg)

    def __destroy__(self):
        self.logFile.write('Destroying...')
        self.logFile.close()
