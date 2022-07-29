import sys

from src.client import Client

if __name__ == '__main__':
    try:
        ip = sys.argv[1]
        port = int(sys.argv[2])
    except IndexError:
        ip = 'localhost'
        port = 6969
    client = Client(ip, port)
    client.run()
