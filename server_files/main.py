import socket
from threading import Thread
import os
import math

clients = []


# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # add 'me> ' to sended message
    def _clear_echo(self, data):
        # \033[F – symbol to move the cursor at the beginning of current line (Ctrl+A)
        # \033[K – symbol to clear everything till the end of current line (Ctrl+K)
        #self.sock.sendall('\033[F\033[K'.encode())
        #data = 'me> '.encode() + data
        # send the message back to user
        self.sock.sendall(data)

    # broadcast the message with name prefix eg: 'u1> '
    def _broadcast(self, data):
        #data = (self.name + '> ').encode() + data
        for u in clients:
            # send to everyone except current client
            if u == self.sock:
                continue
            u.sendall(data)

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):

        # try to read 1024 bytes from user
        # this is blocking call, thread will be paused here

        filename = self.sock.recv(1024).decode('utf-8')
        if filename:
            print("filename:", filename)
        else:
            self.sock.send("File does not exist".encode())
            self._close()
            return

        file_loc = "server_files/" + filename
        try:
            filesize = os.path.getsize(file_loc)
        except:
            self.sock.send("File does not exist".encode())
            self._close()
            return

        self.sock.send(str(filesize).encode())

        Ok = self.sock.recv(1024).decode('utf-8')

        if(Ok != 'Ok'):
            print("Error")

        # unit="K",

        with open(file_loc, "rb") as f:
            count = 0
            while count < filesize:
                # read the bytes from the file
                bytes_read = f.read(1024)
                count += len(bytes_read)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in
                # busy networks
                self.sock.sendall(bytes_read)
                # update the progress bar
                print("\r" + "#" * math.floor(60 * count / filesize) + "-" * (60 - math.floor(60 * count / filesize)) +
                      "|" + str(math.floor(100 * count / filesize)) + "%|", end="")
            print()
        self._close()
        return


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