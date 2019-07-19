# import riaps
from riaps.run.comp import Component
import logging
import random
import os
import time
import spdlog as spd

# CPU limited component

class CPULimit(Component):
    def __init__(self):
        super(CPULimit, self).__init__()
        self.id = random.randint(0,10000)
        logpath = '/tmp/riaps_CPULimit_%d.log' % self.id
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.logger = spd.FileLogger('CPULimit_%d' % self.id, logpath)
        self.logger.set_level(spd.LogLevel.DEBUG)
        self.logger.set_pattern('%v')

        self.logger.info("Starting CPULimit %d" % self.id)

        self.limit = 10000 # min, max ~ 17000
            
    def waste(self):
        self.limit = self.limit + 1000      # Increase limit, do more cycles
        limit = self.limit
        "-".join(str(n) for n in range(self.limit))         
        
    def on_ticker(self):
        trg = self.ticker.recv_pyobj()              # Receive time (as float)
        now = time.time() 
        self.logger.info('Tick %d' % self.limit)
        self.waste()
        
    def handleCPULimit(self):
        self.logger.info('Limit %d' % self.limit)
        self.limit = self.limit - 5000      # Throttle back

    def __destroy__(self):
        self.logger.info("Stopping CPULimit %d" % self.id)
        self.logger.flush()
