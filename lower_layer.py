import logging
import random
import socket

class LowerLayerEndpoint:
    def __init__(self, local_address=None, remote_address=None, 
            loss_probability=0):
        self._local_address = local_address
        self._remote_address = remote_address
        self._loss_probability = loss_probability

        self._socket = socket.socket(type=socket.SOCK_DGRAM)
        if self._local_address is not None:
            self._socket.bind(self._local_address)
        if self._remote_address is not None:
            self._socket.connect(self._remote_address)
            self._local_address = self._socket.getsockname()

        self._shutdown = False

    def send(self, raw_bytes):
        if random.random() >= self._loss_probability:
            result = self._socket.send(raw_bytes)
            logging.debug('Lower layer sent: %s' % raw_bytes)
            return result
        else:
            logging.debug('Lower layer dropped: %s' % raw_bytes)

    def recv(self, max_size=4096):
        if self._remote_address is None:
            try:
                (raw_bytes, address) = self._socket.recvfrom(max_size)
            except OSError:
                return None
            self._remote_address = address
            self._socket.connect(self._remote_address)
        else:
            try:
                raw_bytes = self._socket.recv(max_size)
            except OSError:
                return None

        if len(raw_bytes) == 0:
            return None
        
        logging.debug('Lower layer received: %s' % raw_bytes)
        return raw_bytes

    def shutdown(self):
        if (not self._shutdown):
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
            self._shutdown = True
