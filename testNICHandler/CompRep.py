#CompReq.py
from riaps.run.comp import Component
import os
import random
import logging

class CompRep(Component):
    def __init__(self, logfile):
        super(CompRep, self).__init__()
        self.id = random.randint(0,10000)

        # logpath = '/tmp/riaps_%s_%d.log' % (logfile, self.id)
        # try:
        #     os.remove(logpath)
        # except OSError:
        #     pass
        #
        # self.fh = logging.FileHandler(logpath)
        # self.fh.setLevel(logging.DEBUG)
        # formatter = logging.Formatter("%(message)s")
        # self.fh.setFormatter(formatter)
        # self.logger.addHandler(self.fh)

        self.logger.info("Starting CompRep %d" % self.id)
        self.activeActorCount = 0
        self.activeActors = []

        self.actorName = logfile

    def handleActivate(self):
        self.uuid = self.getUUID()
        self.logger.info("My uuid: %s" % str(self.uuid))

    def on_repPort(self):
        msg = self.repPort.recv_pyobj()
        self.logger.info("Received " + str(self.id) + " %d %s" % msg)
        response = (self.id,2*msg[1])
        self.repPort.send_pyobj(response)


    def on_extHbClock(self):
        msg = self.extHbClock.recv_pyobj()
        self.extHbPub.send_pyobj("REP")

    def on_extHbSub(self):
        msg = self.extHbSub.recv_pyobj()
        if msg not in self.activeActors:
            self.activeActors.append(msg)
            self.activeActorCount += 1
            if self.activeActorCount > 1:
                self.extHbClock.halt()
                self.logger.info("EXTERNAL RUNNING")

    def __destroy__(self):
        self.logger.info("Stopping CompRep %d" % self.id)
