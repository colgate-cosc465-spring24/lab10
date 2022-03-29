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

You will implement a simple sliding window automatic repeat request (ARQ) protocol that transmits data in only one direction (and acknowledgements in the reverse direction). The sender side of the protocol is responsible for: (1) transmitting data packets, (2) guaranteeing the number of "in-flight packets" remains within a fixed bound, and (3) retransmitting data packets if an acknowledgment (ACK) is not received within a pre-determined timeout. The receiver side of the protocol is responsible for sending cumulative ACKs. 

As you work on this lab, you may want to consult the ["Sliding Window" portion of Section 2.5](https://book.systemsapproach.org/direct/reliable.html#sliding-window) of _Computer Networks: A Systems Approach_.

### Packets
The `Packet` class defined in `sliding_window.py` is used to represent a data or acknowledgement (ACK) packet. Every packet contains:
* The character `D` or `A`, which indicates whether it is a <span style="text-decoration:underline;">D</span>ata or <span style="text-decoration:underline;">A</span>CK packet
* A 32-bit sequence number, which indicates which chunk of data the packet contains or which chunk of data is being ACK’d
* Up to 1400 bytes of data (only in data packets)

This object-based representation of a packet can be converted to a sequence of bytes to be sent across the network using the `to_bytes` method. Conversely, a sequence of bytes received from the network can be converted to an object-based representation using the `Packet.from_bytes` method.

The sender and receiver both interact with a simple lower layer protocol that sends and receives packets across the network on behalf of the sliding window ARQ protocol. The `LowerLayerEndpoint` class in `lower_layer.py` exposes a basic API for sending and receiving a packet—really just a sequence of bytes—to/from a "remote" endpoint.

## Implement sender
You are responsible for implementing the sender side of sliding window ARQ protocol by completing the `Sender` class in `sliding_window.py`. 

The sender must do three things:
1. Buffer and send a data packet that is within the window. If the window is full, then the caller (e.g., an application) will be blocked until the packet can be buffered.
2. Retransmit a data packet within the window if it is not acknowledged within a predetermined amount of time.
3. Discard data that has been successfully acknowledged, thus enabling new data to be buffered and sent.

These tasks should be handled by the `_send`, `_retransmit`, and `_recv` functions, respectively, within the `Sender` class. As you write the code, I recommend you add some debugging statements—use the function `logging.debug` instead of `print`—to make it easier to trace your code’s execution.

### `_send`

The `_send` function is invoked by the `send` function which is invoked by an "application" (e.g., `client.py`). The `_send` function needs to:
1. Wait for a free space in the send window—a [semaphore](https://docs.python.org/3.8/library/threading.html#semaphore-objects) is the simplest way to handle this.
2. Assign the chunk of data a sequence number—the first chunk of data is assigned sequence number `0`, and the sequence number is incremented for each subsequent chunk of data.
3. Add the chunk of data to a buffer—in case it needs to be retransmitted.
4. Send the data in a packet with the appropriate type (`D`) and sequence number—use the `Packet` class to construct such a packet and use the `send` method provided by the `LowerLayerEndpoint` class to transmit the packet across the network.
5. Start a retransmission timer—the [Timer](https://docs.python.org/3.8/library/threading.html#timer-objects) class provides a convenient way to do this; the timeout should be 1 second, defined by the constant `Sender._TIMEOUT`; when the timer expires, the `_retransmit` method should be called.

### `_retransmit`
The `_retransmit` function is invoked whenever a retransmission timer—started in `_send` or a previous invocation of `_retransmit`—expires. The `_retransmit` function needs to complete steps 4 and 5 performed by the `_send `function.

### `_recv`
The `_recv` function runs as a separate thread—started when an `Sender` is created—and receives packets from the lower layer until the sender is shutdown. The sender should only receive ACK packets—you should ignore any packets that aren’t ACKs. For every chunk of data that is ACK’d, the `_recv` function needs to:
1. Cancel the retransmission timer for that chunk of data.
2. Discard that chunk of data.
3. Signal that there is now a free space in the send window.

Note that ACKs are cumulative, so even though an ACK packet only contains one sequence number, the ACK effectively acknowledges all chunks of data up to and including the chunk of data associated with the sequence number in the ACK.


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

## Submission instructions
When you are done,  you should commit and push your modified `sliding_window.py` file to GitHub.
