# import riaps
from riaps.run.comp import Component
import logging
import random
import os

class CompTimerPer(Component):
    def __init__(self, logfile):
        super(CompTimerPer, self).__init__()
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

        self.logger.info("Starting CompTimerPer %d" % self.id)

        self.actorName = logfile
        self.messageCounter = 0

    def on_periodic(self):
        now = self.periodic.recv_pyobj()                # Receive time (as float)
        self.ticker.send_pyobj(now)
        per = self.periodic.getPeriod()
        self.logger.info('Periodic %s %s',now,per)
        self.messageCounter += 1
        if self.messageCounter >= 10:
            # self.logger.info('Setting period...')
            self.periodic.setPeriod(5.0)
            if self.messageCounter >= 12:
                self.periodic.halt()
                self.logger.info('Halt')


    def on_restart(self):
        msg = self.restart.recv_pyobj()
        self.periodic.launch()
        self.logger.info('Launch')



    def __destroy__(self):
        self.logger.info('Stopping...')
