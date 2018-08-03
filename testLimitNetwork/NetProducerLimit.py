# import riaps
from riaps.run.comp import Component
import logging
import os
import random

class NetProducerLimit(Component):
    def __init__(self):
        super(NetProducerLimit, self).__init__()
        self.id = random.randint(0,10000)
        logpath = '/tmp/riaps_NetLimit_%d.log' % self.id
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s")
        self.fh.setFormatter(formatter)
        self.logger.addHandler(self.fh)

        self.logger.info("Starting NetLimit %d" % self.id)

        self.blk = 256
        self.size = 0

        self.ticks = 0
        
    def on_ticker(self):
        self.ticks += 1
        self.size = self.size + self.blk

        now = self.ticker.recv_pyobj()   # Receive time.time() as float
        self.logger.info('Tick %d' % self.size)
        msg = bytearray(self.size)
        self.produce.send_pyobj(msg)
        
    def handleNetLimit(self):
        # Ignore double callbacks
        if self.ticks>2:
            self.logger.info('Limit %d' % self.size)
            self.size = 0
            self.ticks = 0

    def __destroy__(self):
        self.logger.info("Stopping NetLimit %d" % self.id)
        
        