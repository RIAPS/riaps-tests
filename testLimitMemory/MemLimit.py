# import riaps
from riaps.run.comp import Component
import logging
import random
import os
import time
import spdlog as spd

# Memory  limited component

class MemLimit(Component):
    def __init__(self):
        super(MemLimit, self).__init__()
        self.id = random.randint(0,10000)
        logpath = '/tmp/riaps_MemLimit_%d.log' % self.id
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.logger = spd.FileLogger('MemLimit_%d' % self.id, logpath)
        self.logger.set_level(spd.LogLevel.DEBUG)
        self.logger.set_pattern('%v')

        self.logger.info("Starting MemLimit %d" % self.id)
        self.chain = []
        self.delta = 35 * 1024 * 1024 # 35MB
        self.size = 0

        self.ticks = 0
            
    def waste(self):
        arr = bytearray(self.delta)
        self.chain.append(arr)
        self.size += self.delta   
        
    def on_ticker(self):
        self.ticks += 1
        self.logger.info('Tick %d' % self.size)
        trg = self.ticker.recv_pyobj() # Receive time (as float)
        now = time.time()
        self.waste()
        
    def handleMemLimit(self):
        if self.ticks > 2: # Ignore back to back warnings
            self.ticks = 0
            self.logger.info('Limit %d' % self.size)
            self.chain = self.chain[:1] # Throttle back  
            self.size = self.delta
   
    def __destroy__(self):
        self.logger.info("Stopping MemLimit %d" % self.id)
        self.logger.flush()