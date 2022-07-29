import socket
import time
import threading


class Client:
    def __init__(self, host: str = 'localhost', port: int = 6969):
        self.addr = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.socket.connect(self.addr)
            print(f'Connected to {self.addr}')
        except ConnectionRefusedError:
            print(f'Connection refused to {self.addr}')
            exit(1)
        except socket.gaierror:  # very gay error
            print(f'Invalid address: {self.addr}')
            exit(1)

    def send(self, data: str | bytes):
        if isinstance(data, str):
            data: bytes = data.encode('utf-8')
        self.socket.send(data)

    def recv(self, size: int) -> str:
        return self.socket.recv(size).decode('utf-8')

    def inbound_loop(self):
        try:
            while True:
                data = self.recv(1024)
                if not data:
                    raise ConnectionResetError
                op, msg = data[:3], data[3:]

                if op == 'MSG':  # Message
                    print(f'[{time.strftime("%H:%M:%S")}] {msg}')
                elif op == 'INV':  # Invalid opcode sent
                    print(f'>>> Invalid command: {msg}')
                elif op == 'ACK':  # good
                    pass
                else:
                    print(f'Unknown opcode [{op}] from server')

        except ConnectionResetError:
            print('Server closed')
        except OSError as e:
            if e.winerror != 10038:
                raise e

    def outbound_loop(self):
        try:
            while True:
                data = input()
                try:
                    if data and data[0] == '/':  # Command
                        if data[1] == '/':  # Message with escaped backslash
                            op = 'MSG'
                            msg = data[1:]
                        else:  # Actual command
                            op = data[1:4].upper()
                            msg = data[5:]
                            if len(data) >= 5 and data[4] != ' ':
                                raise ValueError
                    else:  # Message
                        op = 'MSG'
                        msg = data

                    self.send(f'{op}{msg}')

                except ValueError:
                    print('>>> Invalid command syntax')

        except ConnectionResetError:
            print('Disconnected from server')
        except OSError as e:
            if e.winerror != 10038:
                raise e
        except (KeyboardInterrupt, EOFError):
            print('Received closing signal from inbound thread')
        except UnicodeDecodeError:  # a \xff gets sent to stdin for whatever reason when socket is dead
            pass

    def run(self):
        print(f'Connecting to {self.addr}')
        inbound = threading.Thread(target=self.inbound_loop)
        inbound.daemon = True
        outbound = threading.Thread(target=self.outbound_loop)
        outbound.daemon = True
        self.connect()
        inbound.start()
        outbound.start()
        try:
            while inbound.is_alive() and outbound.is_alive():
                time.sleep(1)

        except (KeyboardInterrupt, EOFError):
            print('Received closing signal from watcher thread')
        print('Shutting down')
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        inbound.join()
        outbound.join(3)
        print('Shut down')
