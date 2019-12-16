#CompPub.py
from riaps.run.comp import Component
import os
import logging
import random
import spdlog as spd

class CompPub(Component):
    def __init__(self, logfile):
        super(CompPub, self).__init__()
        self.id = random.randint(0,10000)

        logpath = '/tmp/riaps_%s_%d.log' % (logfile, self.id)
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.logger = spd.FileLogger('%s_%d' % (logfile, self.id), logpath)
        self.logger.set_level(spd.LogLevel.DEBUG)
        self.logger.set_pattern('%v')

        self.logger.info("Starting CompPub %d" % self.id)

        self.actorName = logfile
        self.messageCounter = 0

    def on_clock(self):
       now = self.clock.recv_pyobj()
       self.logger.info("on_clock(): %s %s" % (now,self.actorName))
       msg = (self.id,self.messageCounter)
       self.PubPort.send_pyobj(msg)
       self.logger.info("Publish %d %s" % msg)
       self.messageCounter += 1


    def __destroy__(self):
        self.logger.info("Stopping CompPub %d" % self.id)
        self.logger.flush()
