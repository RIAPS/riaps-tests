from riaps.run.comp import Component
import logging
import os

class B(Component, logfile):
    def __init__(self):
        super(B, self).__init__()

        logpath = '/tmp/' + logfile + '_CompB.log'
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.testlogger = logging.getLogger(__name__)
        self.testlogger.setLevel(logging.DEBUG)
        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.DEBUG)
        self.testlogger.addHandler(self.fh)

        self.messageCounter = 0

    def on_subPort(self):
        msg = self.subPort.recv_pyobj()
        self.testlogger.info("Subscribe: %s" % msg)

        msg = self.messageCounter
        self.messageCounter += 1

        self.pubPort.send_pyobj(msg)
        self.testlogger.info("Publish: %s" % msg)

    def __destroy__(self):
        self.testlogger.info('Destroying...')
