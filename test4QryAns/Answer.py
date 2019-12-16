#
from riaps.run.comp import Component
import logging
import os
import random
import spdlog as spd

class Answer(Component):
    def __init__(self, logfile):
        super(Answer, self).__init__()
        self.id = random.randint(0,10000)

        logpath = '/tmp/riaps_%s_%d.log' % (logfile, self.id)
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.logger = spd.FileLogger('%s_%d' % (logfile, self.id), logpath)
        self.logger.set_level(spd.LogLevel.DEBUG)
        self.logger.set_pattern('%v')

        self.logger.info("Starting CompAns %d" % self.id)

    def on_srvAnsPort(self):
        msg = self.srvAnsPort.recv_pyobj()
        self.logger.info("Recv %d %d" % msg)
        rep = (self.id, msg[0], msg[1]*2)
        self.logger.info("Answer %d %d %d" % rep)
        self.srvAnsPort.send_pyobj(rep)

    def __destroy__(self):
        self.logger.info("Stopping CompAns %d" % self.id)
        self.logger.flush()
