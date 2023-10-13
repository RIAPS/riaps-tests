#CompPub.py
from riaps.run.comp import Component
import os
import logging
import random
import spdlog as spd

class P2P(Component):
    def __init__(self,id):
        super().__init__()
        self.id = id

        self.logger.info(f"Starting P2P {self.id}")
        self.messageCounter = 0

    def on_clock(self):
       now = self.clock.recv_pyobj()
       msg = (self.id,self.messageCounter)
       self.p2p_pub.send_pyobj(msg)
       self.logger.info(f"{self.id} on_clock(): {now} | publish {msg}")
       self.messageCounter += 1

    def on_p2p_sub(self):
        msg = self.p2p_sub.recv_pyobj()
        self.logger.info(f"{self.id} on_p2p_sub() | connected: {self.p2p_sub.connected()} | msg: {msg}")


    def __destroy__(self):
        self.logger.info(f"Stopping P2P {self.id}")
        self.logger.flush()
