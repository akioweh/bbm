from socket import socket as _socket, SHUT_RDWR
from threading import Thread


class Client:
    def __init__(self, socket: _socket, name: str = 'Unknown'):
        self.socket: _socket = socket
        self.name = self.socket.getpeername()
        self.display_name: str = name
        self.thread: Thread | None = None

    def recv(self, size):
        return self.socket.recv(size).decode('utf-8')

    def send(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.socket.send(data)

    def shut_close(self):
        self.socket.shutdown(SHUT_RDWR)
        self.socket.close()

    def __getattr__(self, item):
        return getattr(self.socket, item)
