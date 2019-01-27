#!/usr/bin/env python

import socket

target_host = "127.0.0.1"
target_port = 80

# create a socket object
client = socket.socket(socket.AF_NET, socket.SOCK_DGRAM)

# sends some data
client.sendto("AAABBBCCC", (target_host, target_port))

# receives some data
data, addr = client.recvfrom(4096)

print data

