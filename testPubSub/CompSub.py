#CompSub.py
from riaps.run.comp import Component
import os
import logging

class CompSub(Component):
    def __init__(self, logfile):
        super(CompSub, self).__init__()
        self.pid = os.getpid()

        logpath = '/tmp/' + logfile + '_CompSub.log'
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.DEBUG)
        self.logger.addHandler(self.fh)

        self.logger.info("(PID %s) - starting CompSub",str(self.pid))

        self.actorName = logfile

    def on_SubPort(self):
        msg = self.SubPort.recv_pyobj()
        self.logger.info("Subscribe %s %s" % (self.actorName,str(msg)))

    def __destroy__(self):
        self.logger.info("(PID %s) - stopping CompSub",str(self.pid))
