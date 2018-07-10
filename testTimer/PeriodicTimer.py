# import riaps
from riaps.run.comp import Component
import logging
import random
import os

class PeriodicTimer(Component):
    def __init__(self, logfile):
        super(PeriodicTimer, self).__init__()

        logpath = '/tmp/' + logfile + '_CompPeriodic.log'
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.DEBUG)
        self.fh.setFormatter(self.logformatter)
        self.logger.addHandler(self.fh)

    def on_periodic(self):
        now = self.periodic.recv_pyobj()                # Receive time (as float)
        self.logger.info('on_periodic():%s',now)
        period = self.periodic.getPeriod()              # Query the period
        if period == 5.0:
            period = period - 1.0
            self.periodic.setPeriod(period)             # Set the period
            self.logger.info('setting period to %f',period)
        msg = now
        self.ticker.send_pyobj(msg)


    def __destroy__(self):
        self.logger.info('Destroying...')
