# import riaps
from riaps.run.comp import Component
import os
import logging
import random

class Query(Component):
    def __init__(self, logfile):
        super(Query, self).__init__()
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

        self.logger.info("Starting CompQry %d" % self.id)

    def on_clock(self):
        now = self.clock.recv_pyobj()   # Receive time.time() as float
        self.logger.info('on_clock(): %s',str(now))
        msg = (self.id,random.randint(0,10000))
        self.logger.info('Query %d %d' % msg)
        self.cltQryPort.send_pyobj(msg)

    def on_cltQryPort(self):
        rep = self.cltQryPort.recv_pyobj()
        self.logger.info('Recv %d %d %d' % rep)

    def __destroy__(self):
        self.logger.info("Stopping CompQry %d" % self.id)
