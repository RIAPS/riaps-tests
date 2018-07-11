#
from riaps.run.comp import Component
import logging
import os

class Server(Component):
    def __init__(self, logfile):
        super(Server, self).__init__()

        logpath = '/tmp/' + logfile + '_CompSrv.log'
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.DEBUG)
        self.fh.setFormatter(self.logformatter)
        self.logger.addHandler(self.fh)

        self.pid = os.getpid()

    def on_srvRepPort(self):
        msg = self.srvRepPort.recv_pyobj()
        self.logger.info("[%d] on_srvRepPort():%s" %(self.pid, msg))
        rep = "clt_req: %d" % self.pid
        self.logger.info("[%d] send rep: %s" % (self.pid,rep))
        self.srvRepPort.send_pyobj(rep)

    def __destroy__(self):
        self.logger.info("[%d] destroyed" % self.pid)
