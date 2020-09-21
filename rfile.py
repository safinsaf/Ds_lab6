import sys
import socket
import os
import math
import ipaddress

# read arguments
filename = sys.argv[1]
host_ip = sys.argv[2]
port = int(sys.argv[3])

print(filename)

#check what we got: ip or hostname, then take ip
try:
    ipaddress.ip_address(host_ip)
except:
    try:
        host_ip = socket.gethostbyname(host_ip)
    except:
        print("Incorrect hostname or IP")

# create the client socket
s = socket.socket()

print(f"[+] Connecting to {host_ip}:{port}")
s.connect((host_ip, port))
print("[+] Connected.")

# check if filename exists
if filename:
    print("filename:", filename)
else:
    print("No file")
    exit()

file_loc = filename

# send filename
s.send(f"{filename}".encode())

#get filesize
try:
    filesize = os.path.getsize(file_loc)
    print("filesize:", filesize)
except:
    print("No such file")
    exit()

Ok = s.recv(1024).decode('utf-8')

# ensure server got size
if(Ok != 'Ok'):
    print("Error")
    exit()


# send file
with open(file_loc, "rb") as f:
    count = 0
    while count < filesize:
        # read the bytes from the file
        bytes_read = f.read(1024)
        count += len(bytes_read)
        if not bytes_read:
            break
        s.sendall(bytes_read)
        # update the progress bar
        print("\r" + "#" * math.floor(60 * count / filesize) + "-" * (60 - math.floor(60 * count / filesize)) +
              "|" + str(math.floor(100 * count / filesize)) + "%|", end="")
    print()

s.close()
