#CompReq.py
from riaps.run.comp import Component
import os
import logging
import random
import threading

class CompReq(Component):
    def __init__(self, logfile):
        super(CompReq, self).__init__()
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

        self.logger.info("Starting CompReq %d" % self.id)

        self.actorName = logfile
        self.messageCounter = 0
        self.lock = threading.Lock()

    def on_clock(self):
        now = self.clock.recv_pyobj()
        self.logger.info("on_clock(): %s %s" % (now,self.actorName))
        if self.lock.acquire(blocking=False):
            msg = (self.id,self.messageCounter)
            try:
                self.reqPort.send_pyobj(msg)
                self.logger.info("Request %d %s" % msg)
                self.messageCounter += 1
            except PortError e:
                self.logger.info("REQ port error")
                self.lock.release()
                self.reset()

    def on_reqPort(self):
        msg = self.reqPort.recv_pyobj()
        self.logger.info("Report " + str(self.id) + " %d %s" % msg)
        self.lock.release()

    def __destroy__(self):
        self.logger.info("Stopping CompReq %d" % self.id)
