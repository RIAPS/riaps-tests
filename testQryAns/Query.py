# import riaps
from riaps.run.comp import Component
import os
import logging

class Query(Component):
    def __init__(self, logfile):
        super(Query, self).__init__()
        self.pid = os.getpid()

        logpath = '/tmp/' + logfile + '_CompQry.log'
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.fh = logging.FileHandler(logpath)
        self.fh.setLevel(logging.DEBUG)
        self.fh.setFormatter(self.logformatter)
        self.logger.addHandler(self.fh)

        self.logger.info("(PID %s) - starting CompQry",str(self.pid))

    def on_clock(self):
        now = self.clock.recv_pyobj()   # Receive time.time() as float
        self.logger.info('on_clock(): %s',str(now))
        msg = "clt_qry:%d" % self.pid
        self.logger.info('[%d] send qry: %s' % (self.pid,msg))
        self.cltQryPort.send_pyobj(msg)

    def on_cltQryPort(self):
        rep = self.cltQryPort.recv_pyobj()
        self.logger.info('[%d] recv rep: %s' % (self.pid,rep))

    def __destroy__(self):
        self.logger.info("[%d] destroyed" % self.pid)
