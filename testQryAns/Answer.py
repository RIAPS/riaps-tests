#
from riaps.run.comp import Component
import logging
import os
import random

class Answer(Component):
    def __init__(self, logfile):
        super(Answer, self).__init__()
        self.id = random.randint(0,10000)

        logpath = '/tmp/riaps_%s_%d.log' % (logfile, self.id)
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s")
        self.fh.setFormatter(formatter)
        self.logger.addHandler(self.fh)

        self.logger.info("Starting CompAns %d" % self.id)

    def on_srvAnsPort(self):
        msg = self.srvAnsPort.recv_pyobj()
        self.logger.info("Recv %d %d" % msg)
        rep = (self.id, msg[0], msg[1]*2)
        self.logger.info("Answer %d %d %d" % rep)
        self.srvAnsPort.send_pyobj(rep)

    def __destroy__(self):
        self.logger.info("Stopping CompAns %d" % self.id)
