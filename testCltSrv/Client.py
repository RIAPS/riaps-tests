# import riaps
from riaps.run.comp import Component
from riaps.run.exc import PortError
import os
import logging
import random

class Client(Component):
    def __init__(self, logfile):
        super(Client, self).__init__()
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

        self.connected = False
        self.pending = 0

        self.logger.info("Starting Client %d" % self.id)

    def on_clock(self):
        now = self.clock.recv_pyobj()   # Receive time.time() as float
        self.logger.info('on_clock(): %s',str(now))
        if self.pending == 0:
            msg = (self.id, random.randint(0,10000))
            try:
                self.cltReqPort.send_pyobj(msg)
                self.logger.info('Req %d %d' % msg)
                self.connected = True
                self.pending += 1
            except PortError:
                if self.connected:
                    self.logger.info('Failed %d %d' % msg)
                else:
                    self.logger.info('Not yet connected!')
        else:
            rep = self.cltReqPort.recv_pyobj()
            self.pending -= 1
            self.logger.info('Rep %d %d %d' % rep)

    def __destroy__(self):
        self.logger.info("Stopping Client %d" % self.id)
