# Lab 10: Sliding Window Automatic Repeat reQuest (ARQ) Simulator

## Overview
In this lab, you will finish implementing the sender side of a simple sliding window Automatic Repeat reQuest (ARQ) protocol.

## Getting started
Clone your git repository on a `tigers` servers. The code provided for this lab is very similar to the code provided for Lab 8, in which you implemented the sender side of a simple stop-and-wait Automatic Repeat reQuest (ARQ) protocol. 

Recall that the `Packet` class (defined in `sliding_window.py`) is used to represent a data or acknowledgement (ACK) packet. A `Packet` object can be converted to a sequence of bytes using the `to_bytes` method, and a sequence of bytes can be converted to Packet object using the `Packet.from_bytes` method. The `LowerLayerEndpoint` class in `lower_layer.py` exposes a basic API for sending and receiving a packet—really just a sequence of bytes—to/from a "remote" endpoint.

As you work on this lab, you may want to consult [Section 2.5.2](https://book.systemsapproach.org/direct/reliable.html#sliding-window) of _Computer Networks: A Systems Approach_.

## Update sender
You are responsible for updating the `Sender` class in `sliding_window.py` to:
1. Limit the number of in-flight packets based on the receiver's advertised window – assume the receiver's initial advertised window is 1
2. Retransmit data packets that are not ACK'd within the timeout (defined by the `_TIMEOUT` constant in the `Sender` class)

## Testing and debugging
To test your code:
1. Start the server using the command: 
```bash
./server.py -p PORT
```
replacing `PORT` with a port number.
2. In a separate terminal window, start the client using the command:
```bash
./client.py -p PORT -h 127.0.0.1
```
replacing `PORT` with the port number you specified when you started the server.
3. Type something into the client and hit enter; the data should appear on the server.

To test your retransmission code, include the command line argument `-l PROBABILITY` (that is a lowercase L) when you start the client and/or the server. Replace `PROBABILITY` with a decimal number between `0.0` to `1.0` (inclusive), indicting the probability that a packet is dropped. If you pass this option to the client, then packets may be dropped. If you pass this option to the server, then ACK packets may be dropped.

By default, the server consumes data as soon as it is available. To change how frequently the server tries to consume data, include the command line argument `-c INTERVAL` when you start the server. Replace `INTERVAL` with a positive decimal number to specify the number of seconds to wait between data consumption.

By default, the receiver's buffer size is 5. To change the receiver's buffer size, include the command line argument `-b SIZE` when you start the server. Replace `SIZE` with a positive integer value.

## Self-assessment
The self-assessment for this lab will be available on Moodle this week. Please complete the self-assessment by 11pm on Monday, April 22nd.
