# Lab 07: Sliding window protocol

## Overview
In this lab, you will implement the sender side of a simple sliding window automatic repeat request (ARQ) protocol.

### Learning objectives
After completing this lab, you should be able to:
* Explain how acknowledgments and timeouts are used to guarantee packets are delivered
* Compute the packets exchanged by a sender and receiver implementing a sliding window algorithm
* Demonstrate the importance of conforming to protocol standards

## Getting started
Clone your git repository on the `tigers` servers. 

As you work on this lab, you may want to consult the ["Sliding Window" portion of Section 2.5](https://book.systemsapproach.org/direct/reliable.html#sliding-window) of _Computer Networks: A Systems Approach_.

## Background

You will implement a simple sliding window (SWP) that transmits data in only one direction (and acknowledgements in the reverse direction). The sender side of the SWP is responsible for: (1) transmitting data packets, (2) guaranteeing the number of “in-flight packets” remains within a fixed bound, and (3) retransmitting data packets if an acknowledgment (ACK) is not received within a pre-determined timeout. The receiver side of the SWP is responsible for sending cumulative ACKs. 

Every SWP packet exchanged between the contains:
* The character `D` or `A`, which indicates whether it is a <span style="text-decoration:underline;">D</span>ata or <span style="text-decoration:underline;">A</span>CK packet
* A 32-bit sequence number, which indicates which chunk of data the packet contains or which chunk of data is being ACK’d
* Up to 1400 bytes of data (only in SWP data packets)

The `SWPPacket` class defined in `swp.py` is used to represent an SWP packet. This object-based representation can be converted to a sequence of bytes to be sent across the network using the `to_bytes` method. Conversely, a sequence of bytes received from the network can be converted to an object-based representation using the `SWPPacket.from_bytes` method.

The SWP sender and receiver both interact with a simple lower layer protocol (LLP) that sends and receives SWP packets across the network on behalf of the SWP. The `LLPEndpoint` class in `llp.py` exposes a basic API for sending and receiving a packet—really just a sequence of bytes—to/from a “remote” endpoint.


---


## Part 1: SWPSender

You are responsible for implementing the sender side of SWP by completing the `SWPSender` class in `swp.py`. 

The sender must do three things:
1. Buffer and send a data packet that is within the send window. If the send window is full, then the caller (e.g., an application) will be blocked until the packet can be buffered.
2. Retransmit a data packet within the send window if it is not acknowledged within a predetermined amount of time.
3. Discard data that has been successfully acknowledged, thus enabling new data to be buffered and sent.

These tasks should be handled by the `_send`, `_retransmit`, and `_recv` functions, respectively, within the `SWPSender` class. As you write the code, I recommend you add some debugging statements—use the function `logging.debug` instead of `print`—`to` make it easier to trace your code’s execution.

### `_send`

The `_send` function is invoked by the `send` function which is invoked by an “application” (e.g., `client.py`). The _send function needs to:

1. Wait for a free space in the send window—a [semaphore](https://docs.python.org/3.7/library/threading.html#semaphore-objects) is the simplest way to handle this.
2. Assign the chunk of data a sequence number—the first chunk of data is assigned sequence number `0`, and the sequence number is incremented for each subsequent chunk of data.
3. Add the chunk of data to a buffer—in case it needs to be retransmitted.
4. Send the data in an SWP packet with the appropriate type (`D`) and sequence number—use the `SWPPacket` class to construct such a packet and use the `send` method provided by the `LLPEndpoint` class to transmit the packet across the network.
5. Start a retransmission timer—the [Timer](https://docs.python.org/3.7/library/threading.html#timer-objects) class provides a convenient way to do this; the timeout should be 1 second, defined by the constant `SWPSender._TIMEOUT`; when the timer expires, the `_retransmit` method should be called.


### `_retransmit`
The `_retransmit` function is invoked whenever a retransmission timer—started in `_send` or a previous invocation of `_retransmit`—expires. The `_retransmit` function needs to complete steps 4 and 5 performed by the `_send `function.

### `_recv`
The `_recv` function runs as a separate thread—started when an `SWPSender` is created—and receives packets from the lower layer protocol (LLP) until the SWP sender is shutdown. The SWP sender should only receive SWP ACK packets—you should ignore any packets that aren’t SWP ACKs. For every chunk of data that is ACK’d, the _recv function needs to:
1. Cancel the retransmission timer for that chunk of data.
2. Discard that chunk of data.
3. Signal that there is now a free space in the send window.

Note that SWP ACKs are cumulative, so even though an SWP ACK packet only contains one sequence number, the ACK effectively acknowledges all chunks of data up to and including the chunk of data associated with the sequence number in the SWP ACK.


### Testing and debugging
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

To test your retransmission code, include the command line argument `-l PROBABILITY` (that is a lowercase L) when you start the client and/or the server. Replace `PROBABILITY` with a decimal number between `0.0` to `1.0` (inclusive), indicting the probability that a packet is dropped. If you pass this option to the client, then ACK packets may be dropped. If you pass this option to the server, then data packets may be dropped.

<!--
To test with loss on the server side, you must download the new server executable:
```
cd executable
	wget https://www.cs.colgate.edu/~agemberjacobson/cosc465/s19/lab03/server.tgz --no-check-certificate
	tar xzf server.tgz
```


## Part 2: SWPReceiver (optional)
If you finish part 1 before the end of lab, then you should work on implementing the receiver side of SWP by completing the `SWPReceiver` class in `swp.py`. 


``


### _recv
```


All functionality for the receiver side of SWP is implemented in the `_recv` function, which runs as a separate thread—started when an `SWPReceiver` is created—and receives packets from the lower layer protocol (LLP). 

For every every SWP data packet that is received, the _recv function needs to:



1. Check if the chunk of data was already acknowledged and retransmit an SWP ACK containing the highest acknowledged sequence number.
2. Add the chunk of data to a buffer—in case it is out of order.
3. Traverse the buffer, starting from the first buffered chunk of data, until reaching a “hole”—i.e., a missing chunk of data. All chunks of data prior to this hole should be placed in the `_ready_data` queue, which is where data is read from when an “application” (e.g., server.py) calls `recv`, and removed from the buffer.
4. Send an acknowledgement for the highest sequence number for which all data chunks up to and including that sequence number have been received.


### Testing and debugging

To test your code:



1. Start the server Python script (**not the server executable**) using the command: \
	<code>./server.py -p <em>PORT \
</em></code>replacing <code><em>PORT</em></code> with a port number from the [range assigned](https://docs.google.com/spreadsheets/d/1wI7dMsgZ3Mlyep5X4I6_vgEadG4ccxG5d37mLNzehyE/edit?usp=sharing) to you or your partner.
2. In a separate terminal window connected to the same birds server, start the client Python script using the command: \
	<code>./client.py -p <em>PORT</em> -h 127.0.0.1</code> \
replacing <code><em>PORT</em></code> with the port number you specified when you started the server.
3. Type something into the client and hit enter; the data should appear on the server.

To test retransmission, include the command line argument <code>-l PROBABILITY</code> (that is a lowercase L) when you start the client and/or the server. Replace <code><em>PROBABILITY</em></code> with a decimal number between 0.0 to 1.0 (inclusive), indicting the probability that a packet is dropped. If you pass this option to the client, then ACK packets may be dropped. If you pass this option to the server, then data packets may be dropped.


---
-->

## Submission instructions

When you are done,  you should commit and push your modified `swp.py` file to GitHub.
