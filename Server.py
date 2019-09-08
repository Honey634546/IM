# coding=utf-8
from socket import *
import threading
import sqlite3
import hashlib
import struct


class Server(object):
    """
    1.register
    2.login
    3.logout
    4.Get the current list of all online users
    5.Group messaging to all online users
    6.Private message to specified user
    7.Without GUI, it can run in Command Line mode
    """

    def __init__(self):
        self.HOST = ""
        self.PORT = 52517
        self.ADDR = (self.HOST, self.PORT)
        self.linklist = []
        self.dick = {}
        server = socket(AF_INET, SOCK_STREAM)
        server.bind(self.ADDR)
        server.listen(1024)
        self.create_sql()
        print('waiting for connection')
        while True:
            client, addr = server.accept()
            self.linklist.append(client)
            data = 'welcome'
            self.send(client, data)
            print(addr, 'connected')
            t = threading.Thread(target=self.tcplink, args=(client, addr))
            t.start()
        server.close()

    def send(self, client, data):
        """
        对发送信息进行包装，解决粘包问题
        向客户端先发送头，在发送信息
        :param client:
        :param data: <str> or <byte>
        :return:
        """
        if isinstance(data, str):
            data = data.encode()
        header = struct.pack('i', len(data))
        client.send(header)
        client.send(data)

    def tcplink(self, client, addr):
        """
        a new tcp link
        :param client:
        :param addr:
        :return:
        """
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
                print(addr, ':', recvdata)
                datas = recvdata.split()
                if datas[0] == "/r":
                    self.register(client, datas)
                elif datas[0] == "/login":
                    self.Log_in(client, datas)
                elif datas[0] == "/logout":
                    self.Log_out(client)
                elif datas[0] == "/showall":
                    self.showall(client)
                elif datas[0] == "/all":
                    self.Mass_msg(recvdata)
                elif datas[0] == "/msg":
                    self.talk(client, recvdata)
                elif datas[0] == "/exit":
                    for k, v in self.dick.items():
                        if v == client:
                            del self.dick[k]
                    self.linklist.remove(client)
                    client.close()
                    print(addr + 'closed')
                    break
                else:
                    data = 'Instruction error'
                    self.send(client, data)
                    # client.send('Instruction error'.encode())
            except ConnectionResetError:
                return

    def create_sql(self):
        """
        创建储存已注册信息的数据库
        :return:
        """
        conn = sqlite3.connect("user_data.db")
        cur = conn.cursor()
        cur.execute(
            """create table if not exists
            %s(
            %s varchar(128) primary key,
            %s varchar(128)
            )"""
            % ('user',
               'account',
               'password'))
        conn.commit()
        cur.close()

    def register(self, client, datas):
        """
        :param client:
        :param datas:
        :return:
        """
        try:
            account = datas[1]
            password = str(datas[2])
            password2 = str(datas[3])
        except BaseException:
            data = 'order error'
            self.send(client, data)
            # client.send('order error'.encode())
            return
        conn = sqlite3.connect("user_data.db")
        cur = conn.cursor()
        data = cur.execute(
            "select * from user where account='%s'" %
            account).fetchone()
        print(data)
        if not data:
            if password == password2:
                # 密码最好加密，不要储存明文密码
                pwd = self.encryption(password)
                cur.execute("insert into user values('%s','%s')"
                            % (account, str(pwd)))
                conn.commit()
                data = 'Successful'
                self.send(client, data)
                # client.send('Successful'.encode())
            else:
                data = 'Two Password Inconsistencies'
                self.send(client, data)
            # client.send('Two Password Inconsistencies'.encode())
        else:
            data = 'User Existing'
            self.send(client, data)
            # client.send("User Existing".encode())
        cur.close()

    def Log_in(self, client, datas):
        """
        登录
        :param client:
        :param datas:
        :return:
        """
        try:
            account = datas[1]
            password = str(datas[2])
            password2 = self.getpassword(account)

            password = self.encryption(password)
        except BaseException:
            data = 'order error'
            self.send(client, data)
            # client.send('order error'.encode())
            return

        if password2 is not None:
            if password == password2:
                self.dick[account] = client
                data = 'Successful'
                self.send(client, data)
                # client.send('Successful'.encode())
            else:
                data = 'Password error'
                self.send(client, data)
                # client.send('Password error'.encode())
        else:
            data = 'No account exists'
            self.send(client, data)
            # client.send('No account exists'.encode())

    def Log_out(self, client):
        """
        登出
        :param client:
        :return:
        """
        for k, v in self.dick.items():
            if v == client:
                del self.dick[k]
                break
        data = 'Offline Success'
        self.send(client, data)
        # client.send("Offline Success".encode())

    def getpassword(self, account):
        """
        :param account:
        :return:
        """
        conn = sqlite3.connect('user_data.db')
        cur = conn.cursor()
        data = cur.execute(
            "select password from user where account='%s'" %
            account).fetchone()
        print(data)
        conn.commit()
        cur.close()
        if data is None:
            return data

        return data[0]

    def showall(self, client):
        """
        显示当前在线用户
        :param client:
        :return:
        """
        for user in self.dick.keys():
            self.send(client, user)
            # client.send(user.encode())

    def Mass_msg(self, data):
        """
        向在线的所有人发消息
        :param data:
        :return:
        """
        datas = data.split(" ", 1)
        for client in self.dick.values():
            try:
                self.send(client, datas[1])
                # client.send(datas[1].encode())
            except BaseException:
                data = 'order error'
                self.send(client, data)
                # client.send('order error'.encode())
                return

    def talk(self, client, data):
        """
        向指定的人发送消息
        :param data:
        :return:
        """
        try:
            datas = data.split(" ", 2)
            sb = datas[1]
            msg = datas[2]
        except BaseException:
            data = 'order error'
            self.send(client, data)
            # client.send('order error'.encode())
            return
        for k, v in self.dick.items():
            if v == client:
                account = k
                break
        try:
            message = account + ":" + msg
            client1 = self.dick.get(sb)
            self.send(client1, message)
            # self.dick.get(sb).send(message.encode())
        except BaseException:
            data = '目标不在线'
            self.send(client, data)

    def encryption(self, password):
        """
        加密密码
        :param password: enable password
        :return: Ciphertext password
        """
        h = hashlib.md5()
        h.update(password.encode())
        return h.hexdigest()


if __name__ == '__main__':
    server = Server()
