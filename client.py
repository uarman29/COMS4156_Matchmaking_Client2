import socket

def main():
    ClientMultiSocket = socket.socket()
    host = '127.0.0.1'
    port = 2022
    print('Waiting for connection response')
    try:
        ClientMultiSocket.connect((host, port))
    except socket.error as e:
        print(str(e))
    res = ClientMultiSocket.recv(1024)
    Input = input('Enter Email: ')
    ClientMultiSocket.send(str.encode(Input))
    res = ClientMultiSocket.recv(1024)
    print(res.decode('utf-8'))
    ClientMultiSocket.close()

main()