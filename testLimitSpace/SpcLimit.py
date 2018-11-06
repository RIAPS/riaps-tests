# import riaps
from riaps.run.comp import Component
import logging
import random
import os
import time
import random, string

# Space  limited component

def remove(file):
    try:
        os.remove(file)
    except OSError:
        pass

class SpcLimit(Component):
    def __init__(self):
        super(SpcLimit, self).__init__()
        self.id = random.randint(0,10000)
        logpath = '/tmp/riaps_SpcLimit_%d.log' % self.id
        remove(logpath)

        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(message)s")
        self.fh.setFormatter(formatter)
        self.logger.addHandler(self.fh)

        self.logger.info("Starting SpcLimit %d" % self.id)
        self.chain = []
        self.delta = 1 # 1 MB
        self.size = self.delta
        self.name = '/tmp/tmp.junk'
        remove(self.name)

        self.ticks = 0

            
    def waste(self):
        cmd = 'dd if=/dev/zero of=%s bs=1M count=%d' % (self.name,self.size)
        res = os.system(cmd)
        if res == 0:
            self.size += self.delta
        else:
            self.logger.info("Failed %d" % (self.size))
        
    def on_ticker(self):
        self.ticks += 1
        trg = self.ticker.recv_pyobj()              # Receive time (as float)
        now = time.time() 
        self.logger.info('Tick %d' % self.size)
        self.waste()
        
    def handleSpcLimit(self):
        # Ignore double callbacks
        if self.ticks > 1:
            self.logger.info('Limit %d' % self.size)
            remove(self.name)
            self.size = self.delta
            self.ticks = 0
   
    def __destroy__(self):
        remove(self.name)
        self.logger.info("Stopping SpcLimit %d" % self.id)