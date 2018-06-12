#
from riaps.run.comp import Component
import logging
import os

class Server(Component, logfile):
    def __init__(self):
        super(Server, self).__init__()

        logpath = '/tmp/' + logfile + '_CompSrv.log'
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

    def on_srvRepPort(self):
        msg = self.srvRepPort.recv_pyobj()
        self.testlogger.info("[%d] on_srvRepPort():%s" %(self.pid, msg))
        rep = "clt_req: %d" % self.pid
        self.testlogger.info("[%d] send rep: %s" % (self.pid,rep))
        self.srvRepPort.send_pyobj(rep)

    def __destroy__(self):
        self.testlogger.info("[%d] destroyed" % self.pid)
