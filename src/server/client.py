from socket import socket as _socket, SHUT_RDWR
from threading import Thread


class Client:
    """client model class providing data storage and methods for socket communication"""
    def __init__(self, socket: _socket, name: str = 'Unknown'):
        self.socket: _socket = socket
        self.name = self.socket.getpeername()
        self.display_name: str = name
        self.thread: Thread | None = None

    def send(self, data: str | bytes):
        """socket.send() wrapper that also accepts str"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.socket.send(data)

    def recv(self, size: int) -> str:
        """socket.recv() wrapper that decodes to str"""
        return self.socket.recv(size).decode('utf-8')

    def shut_close(self):
        """shuts down and closes socket"""
        self.socket.shutdown(SHUT_RDWR)
        self.socket.close()

    def __getattr__(self, item):
        return getattr(self.socket, item)
