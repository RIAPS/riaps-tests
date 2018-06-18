#CompPub.py
from riaps.run.comp import Component
import os
import logging

class CompPub(Component):
    def __init__(self, logfile):
        super(CompPub, self).__init__()
        self.pid = os.getpid()

        logpath = '/tmp/' + logfile + '_CompPub.log'
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.DEBUG)
        self.fh.setFormatter(self.logformatter)
        self.logger.addHandler(self.fh)

        self.logger.info("(PID %s) - starting CompPub",str(self.pid))

        self.actorName = logfile
        self.messageCounter = 0

    def on_clock(self):
       now = self.clock.recv_pyobj()
       self.logger.info("on_clock(): %s %s" % (now,self.actorName))
       msg = (self.actorName,self.messageCounter)
       self.PubPort.send_pyobj(msg)
       self.logger.info("Publish %s %s" % (self.actorName,self.messageCounter))
       self.messageCounter += 1


    def __destroy__(self):
        self.logger.info("(PID %s) - stopping CompPub",str(self.pid))
