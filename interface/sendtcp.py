# echo-client.py

import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    s.sendall(b"000100300001001003001STN1;STN2")
    data = s.recv(1024)

print(data.decode('utf-8'))







