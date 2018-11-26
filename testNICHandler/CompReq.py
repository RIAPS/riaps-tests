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
        self.uuid = False
        self.activeComponentCount = 0
        self.messageCounter = 0
        self.lockReq = threading.Lock()
        self.lockNIC = threading.Lock()

    def handleActivate(self):
        self.uuid = self.getUUID()
        self.logger.info("My uuid: %s" % str(self.uuid))
        self.activeComponentCount += 1

    def on_clock(self):
        now = self.clock.recv_pyobj()
        self.logger.info("on_clock(): %s %s" % (now,self.actorName))

        if self.lockReq.acquire(blocking = False):
            msg = (self.id,self.messageCounter)
            try:
                self.logger.info("Request %d %s" % msg)
                self.reqPort.send_pyobj(msg)
                self.messageCounter += 1
            except PortError:
                self.logger.info("REQ port error")
                self.lockReq.release()
                self.reqPort.reset()

    def on_sporadic(self):
        now = self.sporadic.recv_pyobj()
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
            self.logger.info("Could not acquire NIC req port")

    def on_reqPort(self):
        msg = self.reqPort.recv_pyobj()
        self.logger.info("Report " + str(self.id) + " %d %s" % msg)
        self.lockReq.release()

    def on_reqNicKill(self):
        msg = self.reqNicKill.recv_pyobj()
        self.logger.info("Report %s" % msg)
        self.lockNIC.release()

    def handleNICStateChange(self, state):
        self.logger.info("New NIC state: %s" % state)

    def handlePeerStateChange(self,state,uuid):
        self.logger.info("Peer %s is %s" % (uuid,state))
        if uuid is not self.uuid and 'on' in str(state):
            self.activeComponentCount += 1
            if self.activeComponentCount >= 2:
                self.sporadic.setDelay(20)
                self.sporadic.launch()

        elif uuid is not self.uuid and 'off' in str(state):
            self.activeComponentCount -= 1

    def __destroy__(self):
        self.logger.info("Stopping CompReq %d" % self.id)
