# The `riaps.comp.handlePeerStateChange()` Test

## Description
`handlePeerStateChange(state, uuid)` tells applications that a node has joined or left the network. When triggered, `state` contains one of `{"on","off"}` and `uuid` contains the peer UUID. 

This test uses a special device component to run `sudo shutdown` on a RIAPS node (call it Node A). After some time, another RIAPS node (Node B) uses a GPIO device to power-on the shutdown node.

Passing criteria:
- Components on Node B call `handlePeerStateChange(state = "off", uuid)` after Node A shuts down
- Components on Node B call `handlePeerStateChange(state = "on", uuid)` after Node A turns back on

## Dependencies
- RIAPS Device Components

## Hardware Setup
