import sys

from src.server import Server

if __name__ == '__main__':
    try:
        ip = sys.argv[1]
        port = int(sys.argv[2])
    except IndexError:
        ip = 'localhost'
        port = 6969
    server = Server(ip, port)
    server.run()
