#
# Trivial server
from riaps.run.comp import Component
import logging
import time
import os

class LocalDeviceManager(Component):
    def __init__(self, name):
        super(LocalDeviceManager, self).__init__()
        self.name = name
        self.logger.info("LocalDeviceManager - starting")
        self.requestCounter = 0

    def on_device_port(self):
        msg = self.device_port.recv_pyobj()    # Receive string
        self.logger.info("Device Response for %s: %s" % (self.name, msg))

    def on_clock(self):
        msg = self.clock.recv_pyobj()      # Receive timestamp
        self.requestCounter += 1
        requestMsg = ("LocalDeviceManager on %s - Device Request: %d" % (self.name, self.requestCounter))
        self.logger.info("on_clock(): %s" % requestMsg)
        self.device_port.send_pyobj(requestMsg)       # Send request to device periodically
