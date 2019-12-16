#CompReq.py
from riaps.run.comp import Component
import os
import random
import logging
import spdlog as spd

class CompRep(Component):
    def __init__(self, logfile):
        super(CompRep, self).__init__()
        self.id = random.randint(0,10000)

        logpath = '/tmp/riaps_%s_%d.log' % (logfile, self.id)
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.logger = spd.FileLogger('%s_%d' % (logfile, self.id), logpath)
        self.logger.set_level(spd.LogLevel.DEBUG)
        self.logger.set_pattern('%v')

        self.logger.info("Starting CompRep %d" % self.id)

        self.actorName = logfile

    def on_repPort(self):
        msg = self.repPort.recv_pyobj()
        self.logger.info("Received " + str(self.id) + " %d %s" % msg)
        response = (self.id,2*msg[1])
        self.repPort.send_pyobj(response)

    def __destroy__(self):
        self.logger.info("Stopping CompRep %d" % self.id)
        self.logger.flush()
