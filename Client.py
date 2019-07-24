from socket import *
import threading
import time


def recvmsg(client):
    while True:
        try:
            rec = client.recv(BUFSIZE).decode()
        except:
            continue
        if rec:
            print(rec)


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
        tcpCliSock.send(data)
    tcpCliSock.close()
