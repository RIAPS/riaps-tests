#CompSub.py
from riaps.run.comp import Component
import os
import logging
import random
import spdlog as spd

class CompSub(Component):
    def __init__(self, logfile):
        super(CompSub, self).__init__()
        self.id = random.randint(0,10000)

        logpath = '/tmp/riaps_%s_%d.log' % (logfile, self.id)
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.logger = spd.FileLogger('%s_%d' % (logfile, self.id), logpath)
        self.logger.set_level(spd.LogLevel.DEBUG)
        self.logger.set_pattern('%v')

        self.logger.info("Starting CompSub %d" % self.id)

        self.actorName = logfile

    def on_SubPort(self):
        msg = self.SubPort.recv_pyobj()
        self.logger.info("Subscribe " + str(self.id) + " %d %s" % msg)

    def __destroy__(self):
        self.logger.info("Stopping CompSub %d" % self.id)
        self.logger.flush()
