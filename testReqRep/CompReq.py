#CompReq.py
from riaps.run.comp import Component
import os
import logging
import random
import threading
import spdlog as spd
from riaps.run.exc import PortError

class CompReq(Component):
    def __init__(self, logfile):
        super(CompReq, self).__init__()
        self.id = random.randint(0,10000)

        logpath = '/tmp/riaps_%s_%d.log' % (logfile, self.id)
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.logger = spd.FileLogger('%s_%d' % (logfile, self.id), logpath)
        self.logger.set_level(spd.LogLevel.DEBUG)
        self.logger.set_pattern('%v')

        self.logger.info("Starting CompReq %d" % self.id)

        self.actorName = logfile
        self.messageCounter = 0
        self.lock = threading.Lock()

    def on_clock(self):
        now = self.clock.recv_pyobj()
        self.logger.info("on_clock(): %s %s" % (now,self.actorName))

        # Check if the our 'request' port is connected, if not, return
        if self.reqPort.connected() == 0:
            self.logger.info('Not yet connected!')
            return

        if self.lock.acquire(blocking=False):
            msg = (self.id,self.messageCounter)
            try:
                self.reqPort.send_pyobj(msg)
                self.logger.info("Request %d %s" % msg)
                self.messageCounter += 1
            except PortError:
                self.logger.info('Not yet connected!')
                self.lock.release()
                self.reqPort.reset()

    def on_reqPort(self):
        msg = self.reqPort.recv_pyobj()
        self.logger.info("Report " + str(self.id) + " %d %s" % msg)
        self.lock.release()

    def __destroy__(self):
        self.logger.info("Stopping CompReq %d" % self.id)
        self.logger.flush()
