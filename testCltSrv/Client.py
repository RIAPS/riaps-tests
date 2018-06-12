# import riaps
from riaps.run.comp import Component
import os
import logging

class Client(Component,logfile):
    def __init__(self):
        super(Client, self).__init__()

        logpath = '/tmp/' + logfile + '_CompClt.log'
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.testlogger = logging.getLogger(__name__)
        self.testlogger.setLevel(logging.DEBUG)
        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.DEBUG)
        self.testlogger.addHandler(self.fh)

        self.pid = os.getpid()
        self.pending = 0

    def on_clock(self):
        now = self.clock.recv_pyobj()   # Receive time.time() as float
        self.testlogger.info('on_clock(): %s',str(now))
        msg = "clt_req: %d" % self.pid
        if self.pending == 0:
            self.testlogger.info('[%d] send req: %s' % (self.pid,msg))
            if self.cltReqPort.send_pyobj(msg):
                self.pending += 1
        else:
            rep = self.cltReqPort.recv_pyobj()
            self.pending -= 1
            self.testlogger.info('[%d] recv rep: %s' % (self.pid,rep))

    def __destroy__(self):
        self.testlogger.info("[%d] destroyed" % self.pid)
