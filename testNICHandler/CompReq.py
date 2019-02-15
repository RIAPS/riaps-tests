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

        self.logger.info("Starting CompReq %d" % self.id)

        self.actorName = logfile
        self.uuid = False
        self.messageCounter = 0

        self.activeComponentCount = 0
        self.activeActorCount = 0
        self.lockReq = threading.Lock()
        self.lockNIC = threading.Lock()

        self.activeComps = []
        self.activeActors = []

    def handleActivate(self):
        self.uuid = self.getUUID()
        self.logger.info("My uuid: %s" % str(self.uuid))
        # self.activeActorCount += 1

    def on_clock(self):
        now = self.clock.recv_pyobj()
        self.logger.info("on_clock(): %s %s" % (now,self.actorName))
        if self.activeComponentCount <= 1:
            return
        if self.sporadic.running():
            pass
        else:
            self.sporadic.setDelay(5.0)
            self.sporadic.launch()
        if self.lockReq.acquire(blocking=False):
            msg = (self.id,self.messageCounter)
            try:
                self.logger.info("Request %d %s" % msg)
                self.reqPort.send_pyobj(msg)
                self.messageCounter += 1
            except PortError:
                self.logger.info("REQ port error")
                self.lockReq.release()
                self.reqPort.reset()
            except Exception as e:
                self.logger.error("ERROR on_clock %s" % str(e))

    def on_sporadic(self):
        now = self.sporadic.recv_pyobj()
        self.logger.info("on_sporadic: %s" % str(now))

        if self.lockNIC.acquire(blocking = False):
            try:
                self.logger.info("Requesting NIC Kill")
                msg = 'kill'
                self.reqNicKill.send_pyobj(msg)
            except PortError:
                self.logger.info("REQ port error")
                self.lockNIC.release()
                self.reqNicKill.reset()
        else:
            pass
            self.logger.info("Could not acquire NIC req port")

    def on_reqNicKill(self):
        msg = self.reqNicKill.recv_pyobj()
        self.logger.info("on_reqNicKill: %s" % msg)
        self.lockNIC.release()

    def on_reqPort(self):
        msg = self.reqPort.recv_pyobj()
        self.logger.info("Report " + str(self.id) + " %d %s" % msg)
        self.lockReq.release()

    def on_extHbClock(self):
        msg = self.extHbClock.recv_pyobj()
        self.extHbPub.send_pyobj("REQ")

    def on_extHbSub(self):
        msg = self.extHbSub.recv_pyobj()
        if msg not in self.activeActors:
            self.activeActors.append(msg)
            self.activeActorCount += 1
            if self.activeActorCount > 1:
                self.extHbClock.halt()
                self.logger.info("EXTERNAL RUNNING")

    def on_intHbClock(self):
        msg = self.intHbClock.recv_pyobj()
        self.intHbPub.send_pyobj("REQ")

    def on_intHbSub(self):
        msg = self.intHbSub.recv_pyobj()
        if msg not in self.activeComps:
            self.activeComps.append(msg)
            self.activeComponentCount += 1
            if self.activeComponentCount > 1:
                self.intHbClock.halt()
                self.logger.info("INTERNAL RUNNING")


    def __destroy__(self):
        self.logger.info("Stopping CompReq %d" % self.id)
