# import riaps
from riaps.run.comp import Component
import os
import logging
import random
import spdlog as spd

class Query(Component):
    def __init__(self, logfile):
        super(Query, self).__init__()
        self.id = random.randint(0,10000)

        logpath = '/tmp/riaps_%s_%d.log' % (logfile, self.id)
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.logger = spd.FileLogger('%s_%d' % (logfile, self.id), logpath)
        self.logger.set_level(spd.LogLevel.DEBUG)
        self.logger.set_pattern('%v')

        self.logger.info("Starting CompQry %d" % self.id)

    def on_clock(self):
        now = self.clock.recv_pyobj()   # Receive time.time() as float
        self.logger.info('on_clock(): %s' % str(now))
        msg = (self.id,random.randint(0,10000))
        self.logger.info('Query %d %d' % msg)
        self.cltQryPort.send_pyobj(msg)

    def on_cltQryPort(self):
        rep = self.cltQryPort.recv_pyobj()
        self.logger.info('Recv %d %d %d' % rep)

    def __destroy__(self):
        self.logger.info("Stopping CompQry %d" % self.id)
        self.logger.flush()
