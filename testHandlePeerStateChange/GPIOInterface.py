# riaps:keep_import:begin
from datetime import timedelta
from riaps.run.comp import Component
import threading
import os
import yaml
import gpiod
import platform
from time import sleep
from PowerOnComp import GPIOStates
import libpy.FastIO as riaps_io
 
# riaps:keep_import:end

class GPIOInterface(Component):

# riaps:keep_constr:begin
    def __init__(self, config):
        super(GPIOInterface, self).__init__()
        # self.activeComps = set()
        self.cfg = None
        self.fastio_threads = []
        self.iogroups = []
        self.configfile = config
        self.logger.info( f"Configuration filename:{self.configfile}" )
        if os.path.exists( config ) :
            # Load config file to setup GPIO
            with open(self.configfile, 'r') as cfglist:
                self.cfg = yaml.safe_load( cfglist )
                keys = self.cfg.keys()
                for k in keys:
                    if str( k ).find("/" ) != -1 :
                        self.logger.info( f"IO Chip Configured : [{k}]" )
                        groups = self.cfg[k].keys()
                        for g in groups:
                            if str(g).upper().find("GROUP") != -1 :
                                self.logger.info( f"Adding group:{g}" )
                                self.iogroups.append( riaps_io.IOGroup( self.cfg, k, g, self.logger ) )

                        for g in self.iogroups:
                            self.logger.info( f"{g}" )
                            pins = g.get_all_pins()
                            for p in pins:
                                self.logger.info(f"{p}")

                # actions = self.cfg["ActionList"]
                # for k in actions:
                #     self.logger.info( f"Logic mapping: {actions[k]}" )
               
        self.logger.info( f"__init__() complete" )
# riaps:keep_constr:end

# riaps:keep_gpio_ans:begin
    def on_gpio_ans(self):
        msg = self.gpio_ans.recv_pyobj()
        for thd in self.fastio_threads:
            plug_identity = self.gpio_cmd_port.get_plug_identity( thd.control_thread().get_plug() )
            self.gpio_cmd_port.set_identity( plug_identity )
            self.gpio_cmd_port.send_pyobj( msg )
# riaps:keep_gpio_ans:end

# riaps:keep_gpio_cmd_port:begin
    def on_gpio_cmd_port(self):
        msg  = self.gpio_cmd_port.recv_pyobj()
        ( eventid, iovalues, timestamp ) = msg
        self.logger.info( f"Received GPIO Event {eventid}->{iovalues}:{timestamp}" )

# riaps:keep_gpio_cmd_port:end

# riaps:keep_gpio_config_sub:begin
    def on_gpio_config_sub(self):
        pass
# riaps:keep_gpio_config_sub:end

    def handleMemberJoined(self,group,memberId):
        self.logger.info(f"handleMemberJoined(): group {group.getGroupName()} added {memberId}, has size {group.groupSize()}")
 
# riaps:keep_impl:begin
    def handleActivate(self):        
        for g in self.iogroups:
            iothd = riaps_io.FastIO(connection=self.gpio_cmd_port, iogroup=g, logger=self.logger)
            self.fastio_threads.append( iothd )
            iothd.create( run=True )

            # if len( g.get_input_pins() ) > 0:
            #     self.logger.info( f"Creating IO event thread for group {g.chipname}:{g.groupname}." )
            #     ithd = riaps_io.GPIOEventThread( g, self.logger )
            #     self.gpio_input_threads.append( ithd )
            #     ithd.start()
            # if len( g.get_output_pins() ) > 0:
            #     self.logger.info( f"Creating IO control thread for group {g.chipname}:{g.groupname}." )
            #     cthd = riaps_io.GPIOControlThread( self.gpio_cmd_port, g, self.logger )
            #     cthd.set_event_thread( ithd )
            #     self.gpio_control_threads.append( cthd )
            #     cthd.start()
        
        
        self.group = self.joinGroup("TheGroup","TheGroupInst")
        # self.logger.info("handleActivate(): joined group[%s]: %s" % (self.group.getGroupName(),str(self.group.getGroupId())))
        # self.logger.info(f"handleActivate(): group size: {self.group.groupSize()}")
        # self.logger.info( f"handleActivate() completed." )

    def __destroy__(self):        
        for thd in self.fastio_threads :
            thd.deactivate()

        for thd in self.fastio_threads :
            if thd.is_alive() :
                thd.join()

        self.logger.info( f"__destroy__() completed." )

# riaps:keep_impl:end