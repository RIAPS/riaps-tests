# riaps:keep_import:begin
from datetime import timedelta
from riaps.run.comp import Component
import threading
import os
import subprocess
import yaml
import platform
from time import sleep
 
# riaps:keep_import:end

class ShutdownDevice(Component):

# riaps:keep_constr:begin
    def __init__(self):
        super(ShutdownDevice, self).__init__()
        # self.activeComps = set()
        self.logger.info( f"__init__() complete" )
# riaps:keep_constr:end

# riaps:keep_countdown:begin
    def on_countdown(self):
        msg  = self.countdown.recv_pyobj()

# riaps:keep_countdown:end

# riaps:keep_int_shutdown:begin
    def on_int_shutdown(self):
        msg = self.int_shutdown.recv_pyobj()
        self.logger.info(f"received {msg}")
        result = subprocess.run('pwd',capture_output=True,shell=True)
        self.logger.info(f"subprocess said: {result.stdout}")
        self.int_shutdown.send_pyobj(result.stdout)
# riaps:keep_int_shutdown:end

    # def on_HBsub(self):
    #     msg = self.HBsub.recv_pyobj()
    #     self.activeComps.add(msg)
        
    # def on_HBtimer(self):
    #     now = self.HBtimer.recv_pyobj()
    #     self.HBpub.send_pyobj("ShutdownDevice")
 
# riaps:keep_impl:begin
    def handleActivate(self):
        self.group = self.joinGroup("TheGroup","TheGroupInst")
        # self.logger.info("handleActivate(): joined group[%s]: %s" % (self.group.getGroupName(),str(self.group.getGroupId())))
        # self.logger.info(f"handleActivate(): group size: {self.group.groupSize()}")

    def handleMemberJoined(self,group,memberId):
        self.logger.info(f"handleMemberJoined(): group {group.getGroupName()} added {memberId}, has size {group.groupSize()}")

    def __destroy__(self):        
        self.logger.info( f"__destroy__() completed." )

# riaps:keep_impl:end