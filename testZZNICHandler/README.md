# NIC Handler Test

This test shuts down the ethernet interface of a RIAPS node and then brings it back up.  When the ethernet state goes down, a component triggering the ethernet state change will look for the change to be signaled (handleNICStateChange) and log it.  

## Testing Logic Summary

The application uses an actor that consists of a controlling component (CompReq) and a device (NicDevice) the executes the system command to bring the ethernet down.  

1) Both components of the actor look for pub messages that indicate when each component is up and running using a heartbeat clock (intHbClock).  Once both components are available, "INTERNAL RUNNING" is logged for each component (separately).  The heartbeat clock is then halted.

2) CompReq will then setup a sporadic timer (8 secs) which when fired will then send a request message to the NicDevice to toggle the ethernet connection (first down and then up).

3) When the NicDevice receives the ethernet change request message (down or up), it will execute a system process ("ifconfig eth0 <down or up>") and send back a "done" message to the CompReq.

> Note: CompReq uses thread locks to allow only one request at a time.
