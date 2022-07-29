import socket
import threading
import time
from contextlib import suppress

from .client import Client


class Server:
    """main server class"""
    def __init__(self, host: str = 'localhost', port: int = 6969):
        self.addr = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind(self.addr)
        except socket.gaierror:  # very gay error indeed
            print(f'Invalid address: {self.addr}')
            exit(1)
        except OSError as e:
            if e.winerror == 10049:
                print(f'Invalid address: {self.addr}')
                exit(1)
            else:
                raise e
        self.socket.listen()
        self.clients: list[Client] = []

    def broadcast(self, msg):
        """send message to all connected clients"""
        for client in self.clients:
            client.send(msg)

    def client_handle_loop(self, client: Client):
        """runs threaded \n
        handles incoming traffic from a client
        and sends outbound traffic if necessary
        """
        try:
            while True:
                data = client.recv(1024)
                if not data:
                    raise ConnectionResetError
                op, msg = data[:3], data[3:]

                if op == 'MSG':  # Message
                    client.send('ACK')
                    self.broadcast(f'MSG{client.display_name}: {msg}')
                elif op == 'SDN':  # Set Display Name
                    print(f'Client [{client.name}] changed name from '
                          f'[{client.display_name}] to [{msg}]')
                    client.display_name = msg
                    client.send('ACK')
                else:
                    print(f'Unknown opcode [{op}] from client [{client.name}]')
                    client.send(f'INV{op}-{msg}')

        except ConnectionResetError:
            pass
        except OSError as e:  # When socket is closed
            if e.winerror != 10038:
                raise e
        print(f'Client [{client.name}] disconnected')
        self.clients.remove(client)
        client.close()

    def accept_loop(self):
        """runs threaded \n
        handles incoming connections
        """
        try:
            while True:
                client_socket, addr = self.socket.accept()
                print(f'Client [{addr}] connected')
                client = Client(client_socket)
                self.clients.append(client)
                self.broadcast(f'MSG[{client.name}] connected')

                thread = threading.Thread(target=self.client_handle_loop, args=(client,))
                thread.daemon = True
                client.thread = thread
                thread.start()
        except OSError as e:  # When socket is closed
            if e.winerror != 10038:
                raise e

    def run(self):
        """
        starts server socket and readily accepts and handles client connections \n
        each client connection is handled in a separate thread

        close server with keyboard interrupt or EOF
        """
        print(f'Server started with port [{self.addr[1]}]')
        thread = threading.Thread(target=self.accept_loop)
        thread.daemon = True
        thread.start()
        try:
            while thread.is_alive():
                time.sleep(1)

        except (KeyboardInterrupt, EOFError):
            pass
        # Extremely cursed shutdown that kinda works but i have no idea how to fix some of the problems that only
        # sometimes arise... whatever jut imagine it works perfectly
        print('Closing server')
        with suppress(OSError):
            self.socket.shutdown(socket.SHUT_RDWR)
        for client in self.clients:
            client.shut_close()
        self.socket.close()
        print('Server closed')
