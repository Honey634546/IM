from socket import *
import threading
import struct


def recvmsg(client):
    while True:
        try:
            recvheader = client.recv(4)
            size = struct.unpack('i', recvheader)[0]
            recv_size = 0
            recvdata = b''
            while recv_size < size:
                data = client.recv(1024)
                recvdata += data
                recv_size += len(data)
            recvdata = recvdata.decode()
        except BaseException:
            continue
        if recvdata:
            print(recvdata)


if __name__ == '__main__':
    HOST = 'localhost'
    PORT = 52517
    BUFSIZE = 1024
    ADDR = (HOST, PORT)

    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    tcpCliSock.connect(ADDR)
    t = threading.Thread(target=recvmsg, args=(tcpCliSock,))
    t.start()
    while True:
        # rec = tcpCliSock.recv(BUFSIZE)
        # if rec:
        # print(rec.decode())
        data = input("").encode()
        header = struct.pack('i', len(data))
        tcpCliSock.send(header)

        tcpCliSock.send(data)
    tcpCliSock.close()
