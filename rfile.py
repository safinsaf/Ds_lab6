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

s.send(f"{filename}".encode())

#get filesize
filesize = s.recv(1024).decode('utf-8')
try:
    filesize = int(filesize)
except:
    print(filesize)
    exit()
s.send("Ok".encode())


# give right name in case of copy
copy = 0
while os.path.isfile(filename):
    if copy == 0:
        copy+=1
    elif copy == 1:
        filename = "001_" + filename
        copy+=1
    else:
        filename = '0' * (3-len(str(copy))) + str(copy) + filename[3:]
        copy+=1

# read data, write to file, draw bar
with open(filename, "wb") as f:
    count = 0
    while count < filesize:
        # read 1024 bytes from the socket (receive)
        bytes_read = s.recv(1024)
        count += len(bytes_read)
        if not bytes_read:
            # nothing is received
            # file transmitting is done
            break
        # write to the file the bytes we just received
        f.write(bytes_read)
        # update the progress bar
        print("\r" + "#"*math.floor(60*count/filesize) + "-"*(60-math.floor(60*count/filesize)) +
              "|" + str(math.floor(100*count/filesize)) + "%|", end = "")
    print()

print("File transfered")

s.close()
