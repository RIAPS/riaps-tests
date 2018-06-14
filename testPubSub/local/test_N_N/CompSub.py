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

        self.started = 0

    def on_SubPort(self):
        msg = self.SubPort.recv_pyobj()
        if self.started != 0:
            self.logger.info("Subscribe %s",str(self.pid), str(msg))

    def on_startup(self):
       now = self.startup.recv_pyobj()
       self.logger.info('PID(%s) - on_startup(): %s',str(self.pid),str(now))
       self.started = 1
       self.startup.halt()

    def __destroy__(self):
        self.logger.info("(PID %s) - stopping CompSub",str(self.pid))
