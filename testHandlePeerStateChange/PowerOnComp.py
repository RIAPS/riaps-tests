# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
import os
import struct
import threading
import time
import zmq
import spdlog as spd
import random
from subprocess import run
# riaps:keep_import:end

class GPIOStates:
    ON = "on"
    OFF = "off"
    UNCHANGED = ""

class GPIOOperations:
    WRITE = "O"
    READ = "I"
    NOOP = ""

class PowerOnComp(Component):
    # riaps:keep_constr:begin
    def __init__(self):
        super(PowerOnComp, self).__init__()
        self.pid = os.getpid()

        self.operation = GPIOOperations.WRITE
        self.cur_state = GPIOStates.UNCHANGED
        self.toggle = True
        self.pin_name = "GPIO_67"

        # self.activeComps = set()

        # self.logfile = "powerOffDevice"
        # logpath = '/tmp/riaps_%s_%d.log' % (self.logfile, self.pid)
        # try:
        #    os.remove(logpath)
        # except OSError:
        #    pass

        # self.loggerName = f"{self.logfile}_{self.pid}"
        # self.logger = spd.FileLogger(self.loggerName, logpath)
        # self.logger.set_level(spd.LogLevel.DEBUG)
        # self.logger.set_pattern('%v')

        self.logger.info("Starting PowerOnComp %d" % self.pid)
    # riaps:keep_constr:end
    

    # riaps:keep_clock:begin
    def on_clock(self):
        now = self.clock.recv_pyobj()   # Receive time (as float)
        self.logger.info(f"on_clock at {now}")

        if self.group.groupSize() < 3:
            return

        self.logger.info(f"TheGroup is ready!")
        # if not self.clock.running():
            # self.logger.warn(f"on_clock called while halted!")
            # return
        # self.clock.halt()

        # if self.toggle :
        #     self.cur_state = GPIOStates.ON
        # else:
        #     self.cur_state = GPIOStates.OFF
        
        # msg = [self.operation, self.pin_name, self.cur_state ]

        # self.toggle = not self.toggle

        # self.gpio_qry.send_pyobj(msg)

        self.shutdown.send_pyobj("SHUTDOWN")

    # riaps:keep_clock:end

    # riaps:keep_shutdown:begin
    def on_shutdown(self):
        msg = self.shutdown.recv_pyobj()
        self.logger.info(f"shutdown received:{msg}")
        self.clock.activate()
    # riaps:keep_shutdown:end

    # def on_HBsub(self):
    #     msg = self.HBsub.recv_pyobj()
    #     self.activeComps.add(msg)
    #     if len(self.activeComps) >= 4:
    #         self.clock.setDelay(3.0)
    #         self.clock.launch()
        
    # def on_HBtimer(self):
    #     now = self.HBtimer.recv_pyobj()
    #     self.HBpub.send_pyobj("PowerOnComp")

    # riaps:keep_gpio_qry:begin
    def on_gpio_qry(self):
        msg = self.gpio_qry.recv_pyobj()
        self.logger.info(f"gpio_qry received:{msg}")
    # riaps:keep_gpio_qry:end

    def handleActivate(self):
        self.group = self.joinGroup("TheGroup","TheGroupInst")
        # self.logger.info("handleActivate(): joined group[%s]: %s" % (self.group.getGroupName(),str(self.group.getGroupId())))
        # self.logger.info(f"handleActivate(): group size: {self.group.groupSize()}")

    def handleMemberJoined(self,group,memberId):
        self.logger.info(f"handleMemberJoined(): group {group.getGroupName()} added {memberId}, has size {group.groupSize()}")


    # riaps:keep_deconstr:begin
    def __destroy__(self):
        self.logger.info("Stopping PowerOnComp %d" % self.pid)
        self.logger.flush()
    # riaps:keep_deconstr:end
