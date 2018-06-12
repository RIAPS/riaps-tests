# import riaps
from riaps.run.comp import Component
import logging
import random
import os

class PeriodicTimer(Component, logfile):
    def __init__(self):
        super(PeriodicTimer, self).__init__()

        logpath = '/tmp/' + logfile + '_CompPeriodic.log'
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.testlogger = logging.getLogger(__name__)
        self.testlogger.setLevel(logging.DEBUG)
        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.DEBUG)
        self.testlogger.addHandler(self.fh)

    def on_periodic(self):
        now = self.periodic.recv_pyobj()                # Receive time (as float)
        self.testlogger.info('on_periodic():%s',now)
        period = self.periodic.getPeriod()              # Query the period
        if period == 5.0:
            period = period - 1.0
            self.periodic.setPeriod(period)             # Set the period
            self.testlogger.info('setting period to %f',period)
        msg = now
        self.ticker.send_pyobj(msg)


    def __destroy__(self):
        self.testlogger.info('Destroying...')
