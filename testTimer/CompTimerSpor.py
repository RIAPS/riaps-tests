
# import riaps
from riaps.run.comp import Component
import logging
import random
import os
import spdlog as spd
import time

class CompTimerSpor(Component):
    def __init__(self, logfile):
        super(CompTimerSpor, self).__init__()
        self.id = random.randint(0,10000)
        self.last = time.time()
        self.messagecounter = 0

        logpath = '/tmp/riaps_%s_%d.log' % (logfile, self.id)
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.logger = spd.FileLogger('%s_%d' % (logfile, self.id), logpath)
        self.logger.set_level(spd.LogLevel.DEBUG)
        self.logger.set_pattern('%v')

        self.logger.info("Starting CompTimerSpor %d" % self.id)

        self.actorName = logfile

    def on_sporadic(self):
        now = self.sporadic.recv_pyobj()            # Receive time (as float)
        self.logger.info("Sporadic %s %s" % (now, now - self.last))
        self.last = now
        self.restarter.send_pyobj(now)


    def on_ticker(self):
        now = self.ticker.recv_pyobj()              # Receive message
        # self.logger.info('Got ticker')
        wait = now - self.last
        self.last = time.time()
        self.messagecounter += 1
        self.sporadic.setDelay(0.5)
        delay1 = self.sporadic.getDelay()
        self.sporadic.setDelay(4.0)
        delay2 = self.sporadic.getDelay()
        if self.messagecounter >= 12:
            self.sporadic.halt()
            self.logger.info('Halt')
        else:
            self.sporadic.cancel()
            self.sporadic.launch()
            self.logger.info("Ticker %s %s %s" % (delay1, delay2, wait))


    def __destroy__(self):
        self.logger.info('Stopping...')
        self.logger.flush()
