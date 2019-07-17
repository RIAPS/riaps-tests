# import riaps
from riaps.run.comp import Component
import spdlog as spd
import random
import os
import time
import random, string
import subprocess

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

        self.logger = spd.FileLogger("testLimitSpace",logpath)
        self.logger.set_level(spd.LogLevel.DEBUG)
        self.logger.set_pattern("%v")

        self.logger.info("Starting SpcLimit %d" % self.id)
        self.chain = []
        self.delta = 1 # 1 MB
        self.size = self.delta
        self.name = '/home/riaps/riaps_apps/test_LimitSpace/tmp.junk'
        remove(self.name)

        self.ticks = 0

            
    def waste(self):
        cmd = 'dd if=/dev/zero of=%s bs=1M count=%d' % (self.name,self.size)
        try:
            res = os.system(cmd)
        except Exception as e:
            self.logger.info("os.system error: %s",str(e))
        #res = subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding='utf-8',shell=True)
        if res == 0:
            self.size += self.delta
        else:
            self.logger.info("Failed %d with error code %d" % (self.size,res))
        
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
        self.logger.flush()
        self.logger.close()
