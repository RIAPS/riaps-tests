# import riaps
from riaps.run.comp import Component
import logging
import random
import os

class SporadicTimer(Component, logfile):
    def __init__(self):
        super(SporadicTimer, self).__init__()

        logpath = '/tmp/' + logfile + '_CompSporadic.log'
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.testlogger = logging.getLogger(__name__)
        self.testlogger.setLevel(logging.DEBUG)
        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.DEBUG)
        self.testlogger.addHandler(self.fh)

    def on_sporadic(self):
        now = self.sporadic.recv_pyobj()            # Receive time (as float)
        self.testlogger.info("on_sporadic() %s",now)
        if self.sporadic.getDelay() == 1.0:         # If delay = 1.0 (i.e. the first firing)
            self.sporadic.setDelay(4.0)             # Change delay to 4.0
            self.sporadic.launch()                  # Launch it again

    def on_ticker(self):
        now = self.ticker.recv_pyobj()              # Receive message
        self.testlogger.info('on_ticker():%s',now)
        if self.sporadic.running():
            self.testlogger.info("canceling sporadic")
            self.sporadic.cancel()
        self.sporadic.setDelay(1.0)                 # Set the sporadic timer delay
        self.sporadic.launch()                      # Launch the sproadic timer

    def __destroy__(self):
        self.testlogger.info('Destroying...')
