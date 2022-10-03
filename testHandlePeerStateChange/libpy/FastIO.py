from sqlite3 import Timestamp
from riaps.run.comp import Component
import threading
import os
import zmq
import yaml
import gpiod
import platform
from time import sleep
from PowerOnComp import GPIOStates
from datetime import time, timedelta
import select
import enum
import re
import operator
# from libpy import TerminalColors as tc
import re
import ast


# supervisor thread comms
sup_r_fd, sup_w_fd = os.pipe()

# control thread comms
ctl_r_fd, ctl_w_fd = os.pipe()

# gpio response comms
gpio_r_fd, gpio_w_fd = os.pipe()

# class contains and create all the threads required for fast GPIO operation
class FastIO( threading.Thread ) :
    def __init__(self, connection, iogroup, logger ):
        threading.Thread.__init__(self)
        self.active = threading.Event()
        self.active.set()
        self.iogroup = iogroup
        self.logger = logger
        self.connection = connection
        self.evt_thd = None
        self.ctl_thd = None
        self.do_run = False
        
    # creates the gpio threads and if run=True, starts the supervisor thread
    # the supervisor thread does not need to be started for this module to operate
    def create(self, run=False):
        self.do_run = run

        outputs  = None
        if len( self.iogroup.get_output_pins() ) > 0 or len( self.iogroup.get_input_pins() ) > 0:
            self.ctl_thd = GPIOControlThread( self.connection, self.iogroup, self.logger )
            self.ctl_thd.start()
            self.evt_thd = GPIOEventThread( self.ctl_thd, self.iogroup, self.logger )
            self.evt_thd.start()           
            if self.do_run :
                self.start()
        else:
            self.logger.info( f"No input or output pins defined. GPIO threads are not started!" )

    # return the control thread ID
    def control_thread(self):
        return self.ctl_thd
    
    #returns the event thread ID
    def event_thread(self):
        return self.evt_thd
    
    # deactivates all thread an shutsdown the module
    def deactivate( self ):
        self.logger.info( f"Deactivating FastIO threads." )
        if self.do_run :
            self.active.clear()
        else:
            self.shutdown()
    
    # signals each thread to terminate and waits until the thread has exited
    def shutdown(self):
        self.logger.info( f"FastIO is shutting down..." )
        if self.ctl_thd != None and self.ctl_thd.is_alive() :
            self.ctl_thd.deactivate()
        if self.evt_thd != None and self.evt_thd.is_alive() :
            self.evt_thd.deactivate()

        if self.ctl_thd != None and self.ctl_thd.is_alive() :
            self.ctl_thd.join()
        if self.evt_thd != None and self.evt_thd.is_alive() :
            self.evt_thd.join()
        self.logger.info( f"FastIO shutdown is complete." )

    # supervisor thread work function
    # can be used for debugging or periodic validation of IO settings
    def run( self ) :
        self.logger.info( f"FastIO supervisor thread is running." )
        c = 0
        s = "AB" 
        i = 0
        pin_str = "O:R2S:ON".ljust(32)
        logic_str = ""

        while self.active.is_set() :
            sleep( 2.0 )
            # if sup_w_fd != None :
            #     if i == 0 :
            #         logic_str = f"L:{s[c]}"
            #         logic_str = logic_str.ljust( 32 )
            #         os.write( sup_w_fd, bytearray( logic_str, "utf-8") )
            #         c =  c + 1
            #         if c >= 2:
            #             c = 0
            #     # else:
            #     #     if i%2 == 0 :
            #     #         pin_str = pin_str.replace("ON","OFF").ljust( 32 )
            #     #     else:
            #     #         pin_str = "O:R2S:ON".ljust(32)

            #     #     os.write( sup_w_fd, bytearray(f"{pin_str}", "utf-8") )

            #     i = i + 1
            #     if i >= 10 :
            #         i = 0
            
        
        self.shutdown()

        self.logger.info( f"FastIO is supervisor thread is exiting..." )

# class that encapsulates and handles GPIO input, output, and event operation
class GPIOEventThread( threading.Thread ):
    def __init__(self, ctlthd, iogroup, logger ):
        threading.Thread.__init__(self)
        self.active = threading.Event()
        self.active.set()
        self.ctlthd = ctlthd
        self.iogroup = iogroup
        self.logger = logger
        self.inputs = None
        self.outputs = None
        self.actionlist = iogroup.get_actions()
        self.logic = {}

    # terminates the gpio event thread
    def deactivate( self ):
        self.active.clear()

    # setup all gpio inputs and outputs based on the gpiod library API
    def setup(self):
        pins = self.iogroup.get_input_pins()
        self.chip = gpiod.chip( self.iogroup.chipname )
        if len( pins ) >  0:
            i_pins = []
            i_names = []
            i_modes = []

            for p in pins:
                i_names.append( p.name )
                i_pins.append( p.num )
                i_modes.append( p.mode )

            # setup inputs. if the input type is appended to the consumer name as follows
            # :F for event falling-edge
            # :R for event rising-edge
            # :B for event rising-edge and falling-edge
            # :I for polled input
            self.inputs = self.chip.get_lines( i_pins )
            idx = 0
            for i in self.inputs:
                self.cfg = gpiod.line_request()
                self.cfg.consumer = i_names[idx]
                self.cfg.request_type = i_modes[idx]
                if self.cfg.request_type == gpiod.line_request.EVENT_FALLING_EDGE :
                    self.cfg.consumer = self.cfg.consumer + ":F"
                elif self.cfg.request_type == gpiod.line_request.EVENT_RISING_EDGE :
                    self.cfg.consumer = self.cfg.consumer + ":R"
                elif self.cfg.request_type == gpiod.line_request.EVENT_BOTH_EDGES :
                    self.cfg.consumer = self.cfg.consumer + ":B"
                else:
                    self.cfg.consumer = self.cfg.consumer + ":I"
                
                i.request( self.cfg )

                idx = idx + 1
        else:
            self.logger.info( f"No pins are configures for input {self.iogroup.groupname}!" )

        # setup all outputs
        pins = self.iogroup.get_output_pins()
        if len(pins) > 0 :
            o_pins = []
            o_names = []
            o_modes = []

            for p in pins:
                o_names.append( p.name )
                o_pins.append( p.num )
                o_modes.append( p.mode )

            self.outputs = self.chip.get_lines( o_pins )
            idx = 0
            for o in self.outputs:
                self.outcfg = gpiod.line_request()
                self.outcfg.consumer = o_names[idx]
                self.outcfg.request_type = o_modes[idx]
                o.request( self.outcfg )
                idx = idx + 1
        else:
            self.logger.info( f"No pins are configured for output {self.iogroup.groupname}!" )

    # gpio input, output, event handling based on gpiod module API
    # this function monitors configured IO and, on an IO input event, analyzes
    # the selected logic statement.  If the resulting logic analysis returns true 
    # this function executes the assigned actions and posts a message to the control thread
    # which is published to the RIAPS application
    def run(self):
        # list of all file descriptors used for IO events
        debug = False
        fds = {}

        symbol_table = None
        ost = None
        logic = None
        action = None
        signal = None
       # setup all IO lines based on the group definitions
        self.setup()
        self.logger.info( f"GPIO Event thread for group {self.iogroup.groupname} is running..." )
        # setup the IO event polling loop
        poller = select.poll()
        # register all IO named ssss:R, ssss:F, or ssss:B where ssss=some_name
        # if i.consumer contains ":F", ":R", or ":B" the IO is event triggered
        if self.inputs is not None:
            for i in self.inputs :
                if i.consumer.find(":I") == -1 :
                    fd = i.event_get_fd()
                    self.logger.info( f"Poller Registering : i={i},i.fd={i.event_get_fd()} i.Offset={i.offset}" )
                    poller.register(fd, select.POLLIN | select.POLLPRI )
                    fds[fd] = i
        # register the inter-thread communication pipes for commands       
        self.logger.info( f"Poller Registering supervisor pipe: {sup_r_fd}" )
        poller.register( sup_r_fd, select.POLLIN | select.POLLPRI )
        self.logger.info( f"Poller Registering control pipe: {ctl_r_fd}" )
        poller.register( ctl_r_fd, select.POLLIN | select.POLLPRI )

        # select the first entry in the dictioinary of logic/actions
        if hasattr(self.actionlist,'get_first_action'):
            logic_entry = self.actionlist.get_first_action()
            if logic_entry != None:
                # set the text format version of the logic ans action elements
                logic = logic_entry["logic"]
                action = logic_entry["action"]
                signal = logic_entry["signal"]
                # set the precalculate symbol table
                symbol_table = logic_entry["symbol_table"]
                # set the formated output action table
                ost = logic_entry["ost"]
            else:
                self.logger.info( f"Event thread cannot operate on logic/action entries!" )            

        # start of thread processing loop
        while self.active.is_set() :
            values = {}
            evts = poller.poll( 1000.0 )
            if evts != None and len(evts) > 0 :
                for e in evts:
                    # process events from the control thread pipe
                    if e[0] == ctl_r_fd :
                        data = os.read( ctl_r_fd, 32 )
                        datastr = str( data, "utf-8" )
                        if datastr.find( "I:" ) != -1:
                            self.logger.info( f"Control message READ_IO received ({datastr})" )
                         # control thread has sent a request to update an output pin
                        elif datastr.find( "O:" ) != -1:
                            strlist = re.split( ":|\s", datastr )                            
                            for o in self.outputs :
                                if o.consumer.find( strlist[1] ) != -1 :
                                    if strlist[2] == GPIOStates.ON :
                                        if debug :
                                            self.logger.info( f"{o.consumer}={strlist[2]}" )
                                        o.set_value( 1 )
                                    elif strlist[2] == GPIOStates.OFF :
                                        if debug :
                                            self.logger.info( f"{o.consumer}={strlist[2]}" )
                                        o.set_value( 0 )  
                                    else:
                                        if debug :
                                            self.logger.info( f"{o.consumer}={strlist[2]}" )
                                    break
                                else:
                                    pass
                         # control thread has sent a logic update
                        elif datastr.find("L:") != -1 :
                            strlist = re.split( ":|\s", datastr )
                            logic_entry = self.actionlist.get_action(strlist[1])
                            if logic_entry != None :
                                logic = logic_entry["logic"]
                                action = logic_entry["action"]
                                signal = logic_entry["signal"]
                                symbol_table = logic_entry["symbol_table"]
                                ost = logic_entry["ost"]
                                l = logic_entry["logic"]
                                a = logic_entry["action"]
                                s = logic_entry["signal"]
                                if debug :
                                    self.logger.info( f"Requested logic ({l} : {a} : {s})" )
                            else:
                                self.logger.info( f"Could not select logic {strlist[1]}" )                                
                        else:
                            pass
                    # process events from the supervisor thread pipe    
                    elif e[0] == sup_r_fd :
                        data = os.read( sup_r_fd, 32 )
                        datastr = str( data, "utf-8" )
                        # supervisor has sent a logic update
                        if datastr.find("L:") != -1 :
                            strlist = re.split( ":|\s", datastr )
                            logic_entry = self.actionlist.get_action(strlist[1])
                            if logic_entry != None :
                                logic = logic_entry["logic"]
                                action = logic_entry["action"]
                                signal = logic_entry["signal"]
                                symbol_table = logic_entry["symbol_table"]
                                ost = logic_entry["ost"]
                                l = logic_entry["logic"]
                                a = logic_entry["action"]
                                s = logic_entry["signal"]
                                if debug :
                                    self.logger.info( f"Requested logic ({l} : {a} : {s})" )
                            else:
                                if debug :
                                    self.logger.info( f"Could not select logic {strlist[1]}" )

                        # supervisor has sent request to update an output pin    
                        elif datastr.find("O:") != -1 :
                            strlist = re.split( ":|\s", datastr )
                            for o in self.outputs :
                                if o.consumer == strlist[1] :
                                    if strlist[2] == "ON" :
                                        o.set_value( 1 )
                                        self.logger.info( f"Set output {o.consumer} to ON" )
                                    elif strlist[2] == "OFF" :
                                        o.set_value( 0 )
                                        self.logger.info( f"Set output {o.consumer} to OFF" )
                                    else:
                                        pass
                    # process IO events
                    else:
                        l = fds[e[0]]
                        le = l.event_read()

                        if self.inputs is not None:
                            for i in self.inputs :
                                csmr, mode = re.split( ":", i.consumer )
                                values[csmr] = ( i.get_value() == 1 )   

                if ost != None and symbol_table != None :    
                    # if an IO event occured evaluate the logic symbol table and take actions
                    if len( values ) > 0:
                        matches = {}
                        if compute( symbol_table, values ) :
                            if debug :
                                self.logger.info( f"ost={ost}" )
                            for o in self.outputs :
                                # self.logger.info( f"output={o.consumer}" )
                                if o.consumer in ost:
                                    if ost[o.consumer] == True :
                                        v = 1
                                    else:
                                        v = 0
                                    o.set_value( v )
                                    matches[o.consumer] = v
                                else:
                                    pass

                            evt_str = f"{signal}\n{matches}\n{Timestamp.now()}"
                            if debug :
                                self.logger.info( f"Match signal: {evt_str}" )
                            # self.ctlthd.get_plug().send_pyobj( evt_str )
                            evt_str = evt_str.ljust( 512 )
                            os.write( gpio_w_fd, bytearray( evt_str, "utf-8") )
                            # self.logger.info( f"GPIO RIAPS Signal: {evt_str}" )
                            # self.logger.info( f"Logic inputs match: {logic}" )
                            # self.logger.info( f"Input States = {values}" )

                            ####### debug for timing testing
                            # for o in self.outputs :
                            #     if o.consumer == "R1S" :
                            #         o.set_value(0)
                            ####### debug for timing testing
                        else:
                            if debug :
                                self.logger.info( f"Logic inputs do not match: {logic}" )
                                self.logger.info( f"Input States = {values}" )
        
        # exiting the Event thread run loop
        self.logger.info( f"GPIO Event thread for group {self.iogroup.groupname} is exiting..." )

# This class encapsulates the interface between the RIAPS device and the 
# gpio event and monitoring thread.
# The work function of this class accepts commands from a RIAPS ZMQ plug 
# and communicates these commands to the GPIOEventThread via OS pipe
class GPIOControlThread( threading.Thread ):
    def __init__(self, connection, iogroup, logger ):
        threading.Thread.__init__(self)
        self.conn = connection
        self.active = threading.Event()
        self.active.set()
        self.plug = None
        self.poller = None
        self.iogroup = iogroup
        self.logger = logger
        self.arch = platform.machine()
        self.logger.info( f"Machine architecture is [{self.arch}]" )

    # terminates the Control Thread
    def deactivate( self ):
        self.active.clear()

    # returns the ZMQ plug ID
    def get_plug( self ):
        return self.plug

    # setup the thread communication  
    def setup(self):
        self.plug = self.conn.setupPlug(self)
        self.poller = zmq.Poller()
        self.poller.register( self.plug, zmq.POLLIN )        
        self.poller.register( gpio_r_fd, zmq.POLLIN )        

    # work function for the control thread
    def run(self):
        c = 0
        ctl_str = ""
        self.setup()
        self.logger.info( f"GPIO Control thread for group {self.iogroup.groupname} is running..." )
        if self.plug != None :
            while self.active.is_set() :
                s = dict( self.poller.poll( 1000.0 ) )
                if len(s) > 0 :
                    # process events from the GPIOEvent Thread
                    if gpio_r_fd in s:
                        data = os.read( gpio_r_fd, 512 )
                        datastr = str( data, "utf-8" ).strip()
                        strlist = re.split( "\n", datastr )
                        eventid = strlist[0]
                        iovalues = self.str_to_dict( strlist[1] )
                        timestamp = strlist[2]
                        msg = ( eventid, iovalues, timestamp )
                        self.plug.send_pyobj( msg )
                    else:
                        # relay RIAPS command to the GPIOEventThread
                        msg = self.plug.recv_pyobj()
                        (iocmd, ioname, iostate) = msg
                        if ctl_w_fd != None :
                            ctl_str = f"{iocmd}:{ioname}:{iostate}"
                            ctl_str = ctl_str.ljust( 32 )
                            os.write( ctl_w_fd, bytearray( ctl_str, "utf-8") )
        
        self.logger.info( f"GPIO Control thread for group {self.iogroup.groupname} is exiting..." )

    def str_to_dict( self, strdict:str ) :
        d = {}
        strdict = strdict.replace("{", "")
        strdict = strdict.replace("}", "")
        # self.logger.info( f"strdict={strdict}" )
        entries = re.split(",", strdict)
        # self.logger.info( f"entries={entries}" )
        for e in entries :
            # self.logger.info( f"e={e}" )
            key, value = re.split( ":", e )
            if key.find( "\'") != -1 :
                key = key.replace("\'", "")
            if value.find( "\'") != -1 :
                value = value.replace("\'", "")
            key = key.strip()
            value = value.strip()
            d[key] = value
        return d

# encapsulates all logic and actions for a group
class IOActions:
    def __init__(self, config, chipname, groupname, logger ):
        self.chipname = chipname
        self.groupname = groupname
        self.logger = logger
        self.astlist = {}
        self.actionkeys = []

        try:
            actionlist = dict( config[self.chipname][self.groupname]["ActionList"] )
            self.actionkeys = list( actionlist.keys() )
            for s in actionlist:
                self.add_action( s, actionlist[s]["logic"], actionlist[s]["action"], actionlist[s]["signal"] )
        except KeyError as ex :
            self.logger.info( f"KeyError={ex}" )

    # returns a dictionary of IO Names and desired states for a logic expression evaluation of True  
    def map_output_actions( self, actionstr ) :
        ost = {}
        strs = re.split( ",", actionstr )
        for s in strs :
            strs2 = re.split( "=", s )    
            statestr = strs2[1].upper().strip()
            namestr = strs2[0].strip()
            ost[namestr] = (statestr == "ON")
        return ost

    # string output format if the object is printed 
    def __str__(self):
        text = f"IO Actions->{self.chipname}:{self.groupname}\n"
        for i in self.astlist:
            l = self.astlist[i]["logic"]
            a = self.astlist[i]["action"]
            s = self.astlist[i]["signal"]
            text = text + f"AST Setup for {i} -> {l} : {a} : {s}\n"
        return text

    # get the first action/logic entry
    # return: the first action symbol table entry or None on failure
    def get_first_action( self ):
        a = None
        keys = self.get_action_keys()
        if len( keys ) > 0 :
            a = self.astlist[ keys[0] ]
        return a

    # get a list of action names
    def get_action_keys( self ):
        return self.actionkeys

    # get a specific action symbol table 
    # name : the name of the logic/action entry
    # return: the action symbol table entry or None on failure
    def get_action( self, name ):
        for a in self.astlist:
            if a == name :
                return self.astlist[a]
        return None        

    # add a new action/logic entry
    # name: name of the entry
    # logic: logic expression in the form "P8_14 && ~P8_17"
    # action: action to be taken in the form "P8_1=ON, P8_2=OFF"
    # signal: a signal event to RIAPS posted on successful action taken
    # return True if the entry is added successfully
    def add_action( self, name, logic, action, signal="RIAPS" ):
        success = False
        n = len(self.astlist)
        try:
            self.astlist[name] = {}
            self.astlist[name]["logic"] = logic
            self.astlist[name]["action"] = action
            self.astlist[name]["signal"] = signal
            self.astlist[name]["symbol_table"] = parse( logic )
            self.astlist[name]["ost"] = self.map_output_actions( action )
            outs = self.astlist[name]["ost"]
            self.logger.info( f"Added action {name}-> {logic}:{outs}:{signal}" )
        except KeyError as e:
            if len( self.astlist ) > n:
                del self.astlist[name]
            self.logger( f"Error adding action {name} : {e}" )

        if len( self.astlist ) > n:
            success = True        

        return success

    # delete a specific action/logic entry
    # name: the name of the entry to delete
    # return True if the entry was deleted
    def delete_action( self, name ):
        success = False
        n = len(self.astlist)
        try:
            self.astlist[name]
            del self.astlist[name]    
        except KeyError as e:
            self.logger( f"Error deleting action {name} : {e}" )

        if len( self.astlist ) < n:
            success = True        

        return success

# encapsulates a group of IO and logid/actions operated on by a single control thread
class IOGroup:
    def __init__(self, config, chipname, groupname, logger ):
        self.chipname = chipname
        self.groupname = groupname
        self.group = config[chipname][groupname]
        self.pins = []
        self.outputs = []
        self.inputs = []
        self.actions = {}
        self.logger = logger

        pinkeys = self.group.keys()
        pinnames = list( pinkeys )
        # pinnames.remove( "ActionList" )
        self.logger.info( f"Pins found:{pinnames}" )
        for pin in pinkeys:
            if pin != "ActionList" :
                num = self.group[pin]["PinNum"]
                mode = getattr( gpiod.line_request, self.group[pin]["PinDir"] )
                flags = self.get_flags( self.group[pin]["PinFlags"] )
                logic = self.group[pin]["LogiceMode"]
                iopin = IOPin(self.chipname, pin, num, mode, flags, logic )
                self.pins.append( iopin )
                if iopin.mode == gpiod.line_request.DIRECTION_OUTPUT:
                    self.outputs.append( iopin )
                else:
                    self.inputs.append( iopin )
            else:
                self.actions = IOActions( config, self.chipname, self.groupname, self.logger )
                self.logger.info( f"actions={self.actions}" )

    # set a new the action dictionary
    def set_actions( self, actions : IOActions = {} ):
        self.actions = actions

    # get the action dictionary
    def get_actions( self ):
        return self.actions

    # get a list of all pins
    def get_all_pins(self):
        return self.pins

    # return a list of output pins
    def get_output_pins(self):
        return self.outputs

    # return a list of input pins
    def get_input_pins(self):
        return self.inputs

    def __str__(self):
        return f"IO Group-> chip:{self.chipname} group:{self.groupname} num pins:{len(self.pins)}"

    def get_flags( self, flags ):
        result=0
        for f in flags:
            result |= getattr( gpiod.line_request, f )
        return result

# encapsulates the information and settings for an IO pin
class IOPin:
    def __init__(self, chipname, name, num, mode, flags, logic ):
        self.chipname = chipname
        self.name = name
        self.mode = mode
        self.flags = flags
        self.logic = logic
        self.num = num
        self.line = None
        self.fd = None
    
    def __str__(self):
        return f"IO Pin-> chip:{self.chipname} name:{self.name} num:{self.num} mode:{self.mode} flag:{self.flags} logic:{self.logic}"
        
    def open( self ):
        self.chip = gpiod.chip( self.chipname )
        self.line = self.chip.get_line(self.num)
        request = gpiod.line_request()
        request.consumer = self.name
        request.request_type = self.mode
        request.flags = self.flags
        self.line.request(request)
        if( self.mode == gpiod.line_request.EVENT_RISING_EDGE or 
            self.mode == gpiod.line_request.EVENT_FALLING_EDGE or
            self.mode == gpiod.line_request.EVENT_BOTH_EDGES        ):
            self.fd = self.line.event_get_fd() 
        return self.fd

###################################################################################
# Logic operations Parser and evaluation functions
###################################################################################
class TokenType(enum.Enum):
    T_SYM = 0
    T_NOT = 1
    T_OR = 2
    T_AND = 3
    T_LPAR = 4
    T_RPAR = 5
    T_END = 99

class Node:
    def __init__(self, token_type, value=None):
        self.token_type = token_type
        self.value = value
        self.children = []
    def __repr__(self):
        pass

class Lexer:
    def __init__(self):        
        self.rules = [
            ('ID',  r'[a-zA-Z]\w*'),    # IDENTIFIERS
            ('NOT', r'\~'),             # not 
            ('OR', r'\|\|'),            # or
            ('AND', r'&&'),             # and
            ('LPAR', r'\('),            # (
            ('RPAR', r'\)'),            # )
            ('SKIP', r'[ \t]+'),        # SPACE and TABS
            ('MISMATCH', r'.'),         # ANOTHER CHARACTER
        ]
        self.tokens_join = '|'.join('(?P<%s>%s)' % x for x in self.rules)
        self.token_map = { 
            'ID'    : TokenType.T_SYM, 
            'NOT'   : TokenType.T_NOT, 
            'OR'    : TokenType.T_OR,
            'AND'   : TokenType.T_AND,
            'LPAR'  : TokenType.T_LPAR, 
            'RPAR'  : TokenType.T_RPAR
            }
        
    def lexical_analysis(self,code):
        tokens = [] 
        for m in re.finditer(self.tokens_join, code):
            token_type = m.lastgroup
            token_lexeme = m.group(token_type)

            if token_type == 'SKIP':
                continue
            elif token_type == 'MISMATCH':
                raise RuntimeError('%r unexpected' % token_lexeme)
            else:
                tokens.append(Node(self.token_map[token_type],value=token_lexeme))
                # print('Token = {0}, Lexeme = \'{1}\''.format(token_type, token_lexeme))
                
        tokens.append(Node(TokenType.T_END))
        return tokens

lexer = Lexer()

def match(tokens, token):
    if tokens[0].token_type == token:
        return tokens.pop(0)
    else:
        raise Exception('Invalid syntax on token {}'.format(tokens[0].token_type))


def parse_e(tokens):
    left_node = parse_e2(tokens)
    while tokens[0].token_type == TokenType.T_OR:
        node = tokens.pop(0)
        node.children.append(left_node)
        node.children.append(parse_e2(tokens))
        left_node = node

    return left_node


def parse_e2(tokens):
    left_node = parse_e3(tokens)

    while tokens[0].token_type == TokenType.T_AND:
        node = tokens.pop(0)
        node.children.append(left_node)
        node.children.append(parse_e3(tokens))
        left_node = node

    return left_node


def parse_e3(tokens):
    if tokens[0].token_type == TokenType.T_SYM:
        return tokens.pop(0)
    elif tokens[0].token_type == TokenType.T_NOT:
        node = tokens.pop(0)
        node.children.append(parse_e(tokens))
        return node
    else:
        match(tokens, TokenType.T_LPAR)
        expression = parse_e(tokens)
        match(tokens, TokenType.T_RPAR)

        return expression


def parse(inputstring):
    '''
    Parse the string and constructed a syntax tree.
    '''
    tokens = lexer.lexical_analysis(inputstring)
    symbol_table = parse_e(tokens)
    match(tokens, TokenType.T_END)
    return symbol_table

operations = {
 TokenType.T_NOT : operator.not_,
 TokenType.T_OR : operator.or_,
 TokenType.T_AND : operator.and_
}

def compute(node,values={}):
    '''
    Compute the value of a 'node' constructed by the 
    parser. The 'values' argument is a dictionary containing
    the values of variables.  
    '''
    if node.token_type == TokenType.T_SYM:
        value = values.get(node.value,-1)
        if value == -1:
            raise Exception('Undefined symbol: {}'.format(node.value))
        return value
    left_result = compute(node.children[0],values)
    if len(node.children) > 1:
        right_result = compute(node.children[1],values)
        operation = operations[node.token_type]
        return operation(left_result, right_result)
    else:
        operation = operations[node.token_type]
        return operation(left_result)
