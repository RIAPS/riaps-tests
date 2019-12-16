# import riaps
from riaps.run.comp import Component
import spdlog as spd
import random
import time
import string
import os
from pathlib import Path

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

        self.logger = spd.FileLogger("SpcLimit",logpath)
        self.logger.set_level(spd.LogLevel.DEBUG)
        self.logger.set_pattern("%v")

        self.logger.info("Starting SpcLimit %d" % self.id)
        self.delta = 1 # 1 MB
        self.size = self.delta
        self.ticks = 0

        self.junkpath = '/home/riaps/riaps_apps/test_LimitSpace/tmp.junk'
        Path(self.junkpath).touch()


    def on_ticker(self):
        trg = self.ticker.recv_pyobj()              # Receive time (as float)
        self.ticks += 1
        self.logger.info('Tick %d' % self.size)
        with open(self.junkpath,'ab') as f:
            f.write(bytearray(1000000))

    def handleSpcLimit(self):
        # Ignore double callbacks
        if self.ticks > 1:
            self.logger.info('Limit %d' % self.size)
            self.size = self.delta
            self.ticks = 0
            remove(self.junkpath)
            Path(self.junkpath).touch()

    def __destroy__(self):
        remove(self.junkpath)
        self.logger.info("Stopping SpcLimit %d" % self.id)
        self.logger.flush()
        self.logger.close()
