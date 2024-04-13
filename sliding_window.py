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
    _PACK_FORMAT = '!BII'
    _HEADER_SIZE = struct.calcsize(_PACK_FORMAT)
    MAX_DATA_SIZE = 1400 # Leaves plenty of space for IP + UDP + ARQ header 

    def __init__(self, type, seq_num, adv_win=0, data=b''):
        self._type = type
        self._seq_num = seq_num
        self._adv_win = adv_win
        self._data = data

    @property
    def type(self):
        return self._type

    @property
    def seq_num(self):
        return self._seq_num

    @property
    def adv_win(self):
        return self._adv_win
    
    @property
    def data(self):
        return self._data

    def to_bytes(self):
        header = struct.pack(Packet._PACK_FORMAT, self._type.value, 
                self._seq_num, self._adv_win)
        return header + self._data
       
    @classmethod
    def from_bytes(cls, raw):
        header = struct.unpack(Packet._PACK_FORMAT,
                raw[:Packet._HEADER_SIZE])
        type = PacketType(header[0])
        seq_num = header[1]
        adv_win = int(header[2])
        data = raw[Packet._HEADER_SIZE:]
        return Packet(type, seq_num, adv_win, data)

    def __str__(self):
        if (self._type == PacketType.DATA):
            return "DATA s=%d %s" % (self._seq_num, repr(self._data))
        else:
            return "ACK s=%d w=%d" % (self._seq_num, self._adv_win)

class Sender:
    _TIMEOUT = 1

    def __init__(self, remote_address, loss_probability=0):
        self._ll_endpoint = lower_layer.LowerLayerEndpoint(remote_address=remote_address,
                loss_probability=loss_probability)

        # Data from application that needs to be transmitted
        self._to_transmit = queue.Queue()

        # Sequence number to use for next data packet
        self._next_seq_num = 0

        # Start receive thread
        self._recv_thread = threading.Thread(target=self._recv)
        self._recv_thread.daemon = True
        self._recv_thread.start()

        # Start send thread
        self._send_thread = threading.Thread(target=self._send)
        self._send_thread.daemon = True
        self._send_thread.start()

    def send(self, data):
        for i in range(0, len(data), Packet.MAX_DATA_SIZE):
            self._to_transmit.put(data[i:i+Packet.MAX_DATA_SIZE])

    def _send(self):
        while True:
            data = self._to_transmit.get()
            packet = Packet(PacketType.DATA, self._next_seq_num, data=data)
            self._ll_endpoint.send(packet.to_bytes())
            self._next_seq_num += 1
            logging.debug("Sent: %s" % packet)
        
    def _recv(self):
        while True:
            raw = self._ll_endpoint.recv()
            if raw is None:
                break
            packet = Packet.from_bytes(raw)
            logging.debug("Received: %s" % packet)

class Receiver:
    def __init__(self, local_address, buffer_size=5, loss_probability=0):
        self._ll_endpoint = lower_layer.LowerLayerEndpoint(local_address=local_address, 
                loss_probability=loss_probability)

        self._buffer_size = buffer_size
        self._highest_seq_received = -1
        self._last_seq_consumed = -1
        self._last_seq_signaled = -1
        self._buffer = [None] * buffer_size
        logging.debug("Buffer: %s" % self._buffer)
        self._data_to_consume = threading.Semaphore(0)
        self._lock = threading.Lock()

        # Start receive thread
        self._recv_thread = threading.Thread(target=self._recv)
        self._recv_thread.daemon = True
        self._recv_thread.start()

    def recv(self):
        self._data_to_consume.acquire()
        self._lock.acquire()
        data = self._buffer.pop(0)
        logging.debug("Consume: %s" % data)
        self._last_seq_consumed += 1
        self._buffer.append(None)
        logging.debug("Buffer: %s" % self._buffer)
        self._lock.release()
        return data

    def _recv(self):
        while True:
            # Receive data packet
            raw = self._ll_endpoint.recv()
            if raw is None:
                break
            packet = Packet.from_bytes(raw)
            logging.debug("Received: %s" % packet)

            self._lock.acquire()
            
            if (packet.seq_num > self._last_seq_consumed):
                # Put data in buffer
                slot = packet.seq_num - self._last_seq_consumed - 1
                if (slot >= self._buffer_size):
                    logging.error("Receiver's buffer capacity exceeded; dropping packet")
                    self._lock.release()
                    continue
                logging.debug("Store in slot %d" % slot)
                self._buffer[slot] = packet.data
                logging.debug("Buffer: %s" % self._buffer)
                if (packet.seq_num > self._highest_seq_received):
                    self._highest_seq_received = packet.seq_num
                
                # Tell receiver data is available
                if (packet.seq_num == self._last_seq_signaled + 1):
                    i = slot
                    while (i < self._buffer_size and self._buffer[i] is not None):
                        self._data_to_consume.release()
                        self._last_seq_signaled += 1
                        i += 1

            # Determine advertised window
            occupied = self._highest_seq_received - self._last_seq_consumed
            adv_win = self._buffer_size - occupied

            self._lock.release() 

            # Send ACK
            ack = Packet(PacketType.ACK, packet.seq_num, adv_win)
            self._ll_endpoint.send(ack.to_bytes())
            logging.debug("Sent: %s" % ack)
