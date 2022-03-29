import enum
import logging
import lower_layer
import queue
import struct
import threading

class PacketType(enum.IntEnum):
    DATA = ord('D')
    ACK = ord('A')

class Packet:
    _PACK_FORMAT = '!BI'
    _HEADER_SIZE = struct.calcsize(_PACK_FORMAT)
    MAX_DATA_SIZE = 1400 # Leaves plenty of space for IP + UDP + ARQ header 

    def __init__(self, type, seq_num, data=b''):
        self._type = type
        self._seq_num = seq_num
        self._data = data

    @property
    def type(self):
        return self._type

    @property
    def seq_num(self):
        return self._seq_num
    
    @property
    def data(self):
        return self._data

    def to_bytes(self):
        header = struct.pack(Packet._PACK_FORMAT, self._type.value, 
                self._seq_num)
        return header + self._data
       
    @classmethod
    def from_bytes(cls, raw):
        header = struct.unpack(Packet._PACK_FORMAT,
                raw[:Packet._HEADER_SIZE])
        type = PacketType(header[0])
        seq_num = header[1]
        data = raw[Packet._HEADER_SIZE:]
        return Packet(type, seq_num, data)

    def __str__(self):
        return "%s %d %s" % (self._type.name, self._seq_num, repr(self._data))

class Sender:
    _SEND_WINDOW_SIZE = 5
    _TIMEOUT = 1

    def __init__(self, remote_address, loss_probability=0):
        self._ll_endpoint = lower_layer.LowerLayerEndpoint(remote_address=remote_address,
                loss_probability=loss_probability)

        # Start receive thread
        self._recv_thread = threading.Thread(target=self._recv)
        self._recv_thread.daemon = True
        self._recv_thread.start()

        # TODO: Add additional state variables


    def send(self, data):
        for i in range(0, len(data), Packet.MAX_DATA_SIZE):
            self._send(data[i:i+Packet.MAX_DATA_SIZE])

    def _send(self, data):
        # TODO

        return
        
    def _retransmit(self, seq_num):
        # TODO

        return 

    def _recv(self):
        while True:
            # Receive SWP packet
            raw = self._ll_endpoint.recv()
            if raw is None:
                continue
            packet = Packet.from_bytes(raw)
            logging.debug("Received: %s" % packet)

            # TODO

        return

class Receiver:
    _RECV_WINDOW_SIZE = 5

    def __init__(self, local_address, loss_probability=0):
        self._ll_endpoint = lower_layer.LowerLayerEndpoint(local_address=local_address, 
                loss_probability=loss_probability)

        self._last_ack_sent = 0
        self._max_seq_recv = 0
        self._recv_window = [None] * Receiver._RECV_WINDOW_SIZE

        # Received data waiting for application to consume
        self._ready_data = queue.Queue()

        # Start receive thread
        self._recv_thread = threading.Thread(target=self._recv)
        self._recv_thread.daemon = True
        self._recv_thread.start()

    def recv(self):
        return self._ready_data.get()

    def _recv(self):
        while True:
            # Receive data packet
            raw = self._ll_endpoint.recv()
            packet = Packet.from_bytes(raw)
            logging.debug("Received: %s" % packet)


            # Retransmit ACK, if necessary
            if (packet.seq_num <= self._last_ack_sent):
                ack = Packet(PacketType.ACK, self._last_ack_sent)
                self._ll_endpoint.send(ack.to_bytes())
                logging.debug("Sent: %s" % ack)
                continue

            # Put data in buffer
            slot = packet.seq_num % Receiver._RECV_WINDOW_SIZE
            self._recv_window[slot] = packet.data
            if packet.seq_num > self._max_seq_recv:
                self._max_seq_recv = packet.seq_num

            # Determine what to ACK
            ack_num = self._last_ack_sent
            while (ack_num < self._max_seq_recv):
                # Check next slot
                next_slot = (ack_num + 1) % Receiver._RECV_WINDOW_SIZE
                data = self._recv_window[next_slot]

                # Stop when a packet is missing
                if data is None:
                    break

                # Slot is ACK'd
                ack_num += 1
                self._ready_data.put(data)
                self._recv_window[next_slot] = None

            # Send ACK
            self._last_ack_sent = ack_num
            ack = Packet(PacketType.ACK, self._last_ack_sent)
            self._ll_endpoint.send(ack.to_bytes())
            logging.debug("Sent: %s" % ack)
