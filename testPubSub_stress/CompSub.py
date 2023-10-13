#CompSub.py
from riaps.run.comp import Component
import os
import logging
import random
import spdlog as spd

class CompSub(Component):
    def __init__(self):
        super(CompSub, self).__init__()
        self.id = random.randint(0,10000)

        self.logger.info("Starting CompSub %d" % self.id)

    def on_SubPort(self):
        msg = self.SubPort.recv_pyobj()
        self.logger.info(f"{self.id} on_SubPort() | connected: {self.SubPort.connected()} | msg: {msg}")

    def __destroy__(self):
        self.logger.info("Stopping CompSub %d" % self.id)
        self.logger.flush()
