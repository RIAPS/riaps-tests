#CompSub.py
from riaps.run.comp import Component
import os
import logging
import random

class CompSub(Component):
    def __init__(self, logfile):
        super(CompSub, self).__init__()
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

        self.logger.info("Starting CompSub %d" % self.id)

        self.actorName = logfile

    def on_SubPort(self):
        msg = self.SubPort.recv_pyobj()
        self.logger.info("Subscribe " + str(self.id) + " %d %s" % msg)

    def __destroy__(self):
        self.logger.info("Stopping CompSub %d" % str(self.id))
