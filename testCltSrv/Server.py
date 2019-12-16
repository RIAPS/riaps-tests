#
from riaps.run.comp import Component
from riaps.run.exc import PortError
import logging
import os
import random
import spdlog as spd

class Server(Component):
    def __init__(self, logfile):
        super(Server, self).__init__()
        self.id = random.randint(0,10000)

        logpath = '/tmp/riaps_%s_%d.log' % (logfile, self.id)
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.logger = spd.FileLogger('%s_%d' % (logfile, self.id), logpath)
        self.logger.set_level(spd.LogLevel.DEBUG)
        self.logger.set_pattern('%v')

        self.logger.info("Starting Server %d" % self.id)

    def on_srvRepPort(self):
        msg = self.srvRepPort.recv_pyobj()
        self.logger.info("Req %d %d" % msg)
        rep = (self.id, msg[0], msg[1]*2)
        self.logger.info('Rep %d %d %d' % rep)
        self.srvRepPort.send_pyobj(rep)

    def __destroy__(self):
        self.logger.info("Stopping Server %d" % self.id)
        self.logger.flush()
