#
from riaps.run.comp import Component
import logging
import os
import sys

class A(Component, logfile):
    def __init__(self):
        super(A, self).__init__()

        self.logpath = '/tmp/' + logfile
        self.logFile = open(self.logpath, 'w')
        self.logFile.write('Actor A started\n')

        self.messageCounter = 0

    def on_clock(self):
        msg = self.clock.recv_pyobj()

        msg = self.messageCounter
        self.messageCounter += 1

        self.pubPort.send_pyobj(msg)
        self.logFile.write("Publish: %s\n" % msg)

        self.clock.halt()

    def on_subPort(self):
        msg = self.subPort.recv_pyobj()

        self.logFile.write("Subscribe: %s\n" % msg)

        if (self.messageCounter < 10):
            msg = self.messageCounter
            self.messageCounter += 1

            self.pubPort.send_pyobj(msg)
            self.logFile.write("Publish: %s\n" % msg)

    def __destroy__(self):
        self.logFile.write('Destroying...')
        self.logFile.close()
