
#CompReq.py
from riaps.run.comp import Component
import os
import random
import logging
import subprocess
import time

class NicDevice(Component):
    def __init__(self, logfile):
        super(NicDevice, self).__init__()
        self.id = random.randint(0,10000)

        # logpath = '/home/riaps/riaps_%s_%d.log' % (logfile, self.id)
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

        self.logger.info("Starting NicDevice %d" % self.id)

        self.actorName = logfile
        self.uuid = False
        self.activeComps = []
        self.activeComponentCount = 0

    def handleActivate(self):
        self.uuid = self.getUUID()
        self.logger.info("My uuid: %s" % str(self.uuid))
        # self.activeComponentCount += 1

    def on_repPort(self):
        msg = self.repPort.recv_pyobj()
        self.logger.info("Received %s" % msg)
        self.logger.info("Setting NIC to down...")
        try:
            res = subprocess.call('ifconfig eth1 down',shell=True)
            self.logger.info("DOWN RESULT: %s" % str(res))
            time.sleep(10)
            self.logger.info("Setting NIC to up...")
            res = subprocess.call('ifconfig eth1 up',shell=True)
            self.logger.info("UP RESULT: %s" % str(res))
            response = 'done'
        except Exception as e:
            response = str(e)
        self.repPort.send_pyobj(response)

    def on_intHbClock(self):
        msg = self.intHbClock.recv_pyobj()
        self.intHbPub.send_pyobj("KILL")

    def on_intHbSub(self):
        msg = self.intHbSub.recv_pyobj()
        if msg not in self.activeComps:
            self.activeComps.append(msg)
            self.activeComponentCount += 1
            if self.activeComponentCount > 1:
                self.intHbClock.halt()
                self.logger.info("INTERNAL RUNNING")


    def __destroy__(self):
        self.logger.info("Stopping NicDevice %d" % self.id)
