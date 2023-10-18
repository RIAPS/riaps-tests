#CompPub.py
import json

from riaps.run.comp import Component
import os
import logging
import random
import spdlog as spd

class P2P(Component):
    def __init__(self, node_id: str):
        super().__init__()
        self.id = node_id
        self.connections = {}
        self.connections2 = {}
        self.logger.info(f"Starting P2P {self.id}")
        self.messageCounter = 0

    def on_clock(self):
       now = self.clock.recv_pyobj()
       msg = {"id": self.id, "connections": self.p2p_sub.connected(), "msg_id": self.messageCounter, "topic": "1"}
       self.p2p_pub.send_pyobj(msg)
       msg2 = {"id": self.id, "connections": self.p2p_sub2.connected(), "msg_id": self.messageCounter, "topic": "2"}
       self.p2p_pub2.send_pyobj(msg2)
       self.logger.info(f"{self.id} on_clock(): {now}")
       self.messageCounter += 1

    def on_p2p_sub(self):
        msg = self.p2p_sub.recv_pyobj()
        old_connections = self.connections.get(msg["id"], None)
        current_connections = msg["connections"]
        if old_connections != current_connections:
            self.connections[msg["id"]] = current_connections
            self.logger.info(f"{json.dumps(msg)}")

    def on_p2p_sub2(self):
        msg = self.p2p_sub2.recv_pyobj()
        old_connections = self.connections2.get(msg["id"], None)
        current_connections = msg["connections"]
        if old_connections != current_connections:
            self.connections2[msg["id"]] = current_connections
            self.logger.info(f"{json.dumps(msg)}")

    def __destroy__(self):
        self.logger.info(f"Stopping P2P {self.id}")
        self.logger.flush()
