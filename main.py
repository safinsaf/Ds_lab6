import socket
from threading import Thread
import os

clients = []


# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        #Read filename
        filename = self.sock.recv(1024).decode('utf-8')
        if filename:
            print("filename:", filename)
        else:
            #return error
            self.sock.send("File does not exist".encode())
            self._close()
            return

        # give right name in case of copy
        copy = 0
        while os.path.isfile(filename):
            if copy == 0:
                copy += 1
            elif copy == 1:
                filename = "001_" + filename
                copy += 1
            else:
                filename = '0' * (3 - len(str(copy))) + str(copy) + filename[3:]
                copy += 1

        self.sock.send("Ok".encode())

        # read data, write to file, draw bar
        with open(filename, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)
                bytes_read = self.sock.recv(1024)
                if not bytes_read:
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)

        print("File read")
        self._close()


def main():
    next_name = 1

    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reuse address; in OS address will be reserved after app closed for a while
    # so if we close and imidiatly start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen to all interfaces at 8800 port
    sock.bind(('', 8800))
    sock.listen()
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        # start new thread to deal with client
        ClientListener(name, con).start()


if __name__ == "__main__":
    main()