#
from riaps.run.comp import Component
import logging
import os

class NetConsumer(Component):
    def __init__(self):
        super(NetConsumer, self).__init__()
        self.logger.info("Starting Sink")
        
    def on_consume(self):
        msg = self.consume.recv_pyobj()
        self.logger.info("Consume %d" % len(msg))

    