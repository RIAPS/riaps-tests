# riaps:keep_import:begin
from riaps.run.comp import Component
import logging
import os
import struct
import threading
import time
import zmq
# riaps:keep_import:end


class LocalDeviceThread(threading.Thread):
    '''
    Inner LocalDevice thread
    '''
    def __init__(self,trigger,logger):
        threading.Thread.__init__(self)
        self.logger = logger
        self.active = threading.Event()
        self.active.clear()
        self.waiting = threading.Event()
        self.terminated = threading.Event()
        self.terminated.clear()
        self.trigger = trigger               # inside RIAPS port
        self.plug = None
        self.plug_identity = None
        self.logger.info("LocalDeviceThread _init()_ed")

    def get_identity(self,ins_port):
        if self.plug_identity is None:
            while True:
                if self.plug != None:
                    self.plug_identity = ins_port.get_plug_identity(self.plug)
                    break
                time.sleep(0.1)
        return self.plug_identity

    def run(self):
        self.logger.info("LocalDeviceThread - starting")
        self.plug = self.trigger.setupPlug(self)     # Ask RIAPS port to make a plug (zmq socket) for this end
        self.poller = zmq.Poller()                   # Set up poller to wait for messages from either side
        self.poller.register(self.plug, zmq.POLLIN)  # plug socket (connects to trigger port of parent device comp)
        while 1:
            self.active.wait(None)                   # Events to handle activation/termination
            if self.terminated.is_set(): break
            if self.active.is_set():                 # If we are active
                socks = dict(self.poller.poll(20000.0))  # Run the poller: wait input from either side, timeout if none
                if len(socks) == 0:
                    self.logger.info("LocalDeviceThread timeout")
                if self.terminated.is_set(): break
                if self.plug in socks and socks[self.plug] == zmq.POLLIN:    # Input from the plug
                    message = self.plug.recv_pyobj()
                    self.logger.info("Plug message received: %s" % message)
                    messageNum = message[-1]
                    responseMsg = ("Device Response: %s" % messageNum)
                    self.logger.info("Plug message response: %s" % responseMsg)
                    self.plug.send_pyobj(responseMsg)                        # Send response back to the LocalDevice
        self.logger.info("LocalDeviceThread - ended")


    def activate(self):
        self.active.set()
        self.logger.info("LocalDeviceThread - activated")

    def deactivate(self):
        self.active.clear()
        self.logger.info("LocalDeviceThread - deactivated")

    def terminate(self):
        self.active.set()
        self.terminated.set()
        self.logger.info("LocalDeviceThread - terminating")

class LocalDevice(Component):
    # riaps:keep_constr:begin
    def __init__(self):
        super(LocalDevice, self).__init__()
        self.pid = os.getpid()
        self.logger.info("LocalDevice - starting")
        self.LocalDeviceThread = None  # Cannot manipulate ports in constructor or start threads, use clock pulse
    # riaps:keep_constr:end

# riaps:keep_device_port:begin
    def on_device_port(self):
        # receive
        msg = self.device_port.recv_pyobj()    # required to remove message from queue
        self.logger.info('on_device_port(): %s' % msg)
        self.trigger.send_pyobj(msg)
    # riaps:keep_device_port:end

    # riaps:keep_clock:begin
    def on_clock(self):
        if self.LocalDeviceThread == None: # First clock pulse
            self.LocalDeviceThread = LocalDeviceThread(self.trigger,self.logger) # Inside port, external zmq port
            self.LocalDeviceThread.start() # Start thread
            self.trigger.set_identity(self.LocalDeviceThread.get_identity(self.trigger))
            self.trigger.activate()
        now = self.clock.recv_pyobj()   # Receive time (as float)
        self.clock.halt()               # Halt this timer (don't need it anymore)
    # riaps:keep_clock:end

    # riaps:keep_trigger:begin
    def on_trigger(self):                       # Internally triggered operation (
        msg = self.trigger.recv_pyobj()         # Receive message from internal thread
        self.logger.info("LocalDevice - on_trigger(): %s" % msg)
        self.device_port.send_pyobj(msg)               # Send answer back from original query
    # riaps:keep_trigger:end

    # riaps:keep_deconstr:begin
    def __destroy__(self):
        self.logger.info("__destroy__")
        self.LocalDeviceThread.deactivate()
        self.LocalDeviceThread.terminate()
        self.LocalDeviceThread.join()
        self.logger.info("LocalDevice - __destroy__ed")
    # riaps:keep_deconstr:end

    # riaps:keep_impl:begin
    # riaps:keep_impl:end
