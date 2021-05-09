import socket
import json
import os

from PySide6.QtCore import QThread, QObject, Slot, Signal


class Client:
    def __init__(self, address:tuple=None, host:str=None, port:int=None, debug:bool=False):
        """Create connection to the server.
        :param address: The server address (host, port). Leave None if host and port not None
        :param host: The server host (port). Leave None if address not None
        :param port: The server port (port). Leave None if address not None    
        :param debug: enabled printing errors, if debug is True
        """
        if address is not None:
            self.address = address
        elif host is not None and port is not None:
            self.address = (host, port)
        self.debug = debug

        self.client_socket = self.create_client()
        if self.client and self.debug:
            print('[client debug] - Client socket has been successfully created.')

    def create_client(self) -> socket.socket:
        """Create a client socket object.
        :return: socket object
        """
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return client

    def client_connect(self) -> int:
        """Connect to the server.
        :return: -1 if connection failed otherwise 1
        """
        try:
            self.client_socket.connect(self.address)
        except ConnectionRefusedError:
            if self.debug:
                print('[client debug] - Connection with server has failed.')
            return -1
        else:
            if self.debug:
                print('[client debug] - Connection has been successfully created.')
            return 1

    def client(self) -> socket.socket:
        """Return a client socket object.
        """
        return self.client_socket


class ClientWorker(QObject):
    """Waiting for messages.
    """
    recieved_message = Signal(str)
    def __init__(self, client_socket, parent=None):
        super(ClientWorker, self).__init__(parent)
        self.client_socket = client_socket

    @Slot()
    def start(self):
        while self.client_socket is not None:
            data = self.client_socket.recv(1024)
            if not data:
                break
            else:
                self.recieved_message.emit(data.decode('utf-8'))

    def send(self, data):
        self.client_socket.send(data.encode("utf-8"))

    def close(self):
        self.client_socket.close()
        self.client_socket = None

if __name__ == "__main__":
    # TESTS
    client = Client(host='127.0.0.1', port=8888, debug=True)
    while client.client_connect() == -1:
        continue

    while True:
        pass
