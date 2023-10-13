#CompPub.py
from riaps.run.comp import Component
import os
import logging
import random
import spdlog as spd

class CompPub(Component):
    def __init__(self):
        super().__init__()
        self.id = random.randint(0,10000)

        self.logger.info(f"Starting CompPub {self.id}")
        self.messageCounter = 0

    def on_clock(self):
       now = self.clock.recv_pyobj()
       msg = (self.id,self.messageCounter)
       self.PubPort.send_pyobj(msg)
       self.logger.info(f"{self.id} on_clock(): {now} | publish {msg}")
       self.messageCounter += 1


    def __destroy__(self):
        self.logger.info(f"Stopping CompPub {self.id}")
        self.logger.flush()
