import socket
from datetime import datetime

def print_time(*arg, **kwarg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(timestamp, *arg, **kwarg)

def main():
    PlayerSocket = socket.socket()
    host = '127.0.0.1'
    port = 2022
    print_time('Waiting for connection response')
    try:
        PlayerSocket.connect((host, port))
    except socket.error as e:
        print_time(str(e))
    res = PlayerSocket.recv(1024)
    Input = input('Enter Email: ')
    PlayerSocket.send(str.encode(Input))
    res = PlayerSocket.recv(1024)
    print_time(res.decode('utf-8'))
    PlayerSocket.close()

main()