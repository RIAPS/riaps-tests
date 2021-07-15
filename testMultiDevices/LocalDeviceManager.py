#
# Trivial server
from riaps.run.comp import Component
import logging
import time
import os
import spdlog as spd

class LocalDeviceManager(Component):
    def __init__(self):
        super(LocalDeviceManager, self).__init__()
        self.pid = os.getpid()

        self.logfile = "localDeviceMgr"
        logpath = '/tmp/riaps_%s_%d.log' % (self.logfile, self.pid)
        try:
            os.remove(logpath)
        except OSError:
            pass

        self.logger = spd.FileLogger('%s_%d' % (self.logfile, self.pid), logpath)
        self.logger.set_level(spd.LogLevel.DEBUG)
        self.logger.set_pattern('%v')

        self.logger.info("Starting LocalDeviceManager %d" % self.pid)
        self.requestCounter = 0

    def on_device_port(self):
        msg = self.device_port.recv_pyobj()    # Receive string
        self.logger.info("Recv: %d %d %d" % (msg[0], msg[1], msg[2]))

    def on_clock(self):
        msg = self.clock.recv_pyobj()      # Receive timestamp
        self.requestCounter += 1
        requestMsg = (self.pid, self.requestCounter)
        self.logger.info("Query: %d %d" % requestMsg)
        self.device_port.send_pyobj(requestMsg)       # Send request to device periodically

    def __destroy__(self):
        self.logger.info("Stopping LocalDeviceManager %d" % self.pid)
        self.logger.flush()
