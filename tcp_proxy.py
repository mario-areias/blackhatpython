#!/usr/bin/env python

import sys
import socket
import ssl
import threading
import re
import os

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2

    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x))  for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
        result.append( b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
    print b'\n'.join(result)

def receive_from(connection):
    buffer = ""

    # We set a 2 second timeout; depending on our target, this may need to be adjusted
    connection.settimeout(2)
    try:
        # keep reading into the buffer until there is no more data or we timeout
        while True:
            data = connection.recv(4096)

            if not data:
                break
            
            buffer += data
    except:
        pass
    
    return buffer

# modify request
def request_handler(buffer, remote_host):

    # Updating host header with remote host. To avoid send Host: 127.0.0.1
    buffer = re.sub(r"Host: [a-zA-Z0-9.:]+", "Host: %s" % remote_host, buffer) 

    # Removing gzip header to be able to modify responses easily
    buffer = re.sub("Accept-Encoding: gzip, deflate\r\n", "", buffer)
    return buffer

# modify any responses destined for the local host
def response_handler(buffer):       
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):

    if remote_port == 443:
        sock = socket.socket(socket.AF_INET)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # optional
        remote_socket = context.wrap_socket(sock, server_hostname=remote_host )
        remote_socket.connect((remote_host, remote_port))
    else:
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((remote_host, remote_port))

    if receive_first:

        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # send it to our response handler
        remote_buffer = response_handler(remote_buffer)

        # if we have data to send to our local, send it
        if len(remote_buffer):
            print "[<==] Sending %d bytes to localhost." % len(remote_buffer)
            client_socket.send(remote_buffer)

    # now lets loop and read from local
    # send to remote, send to local
    # rinse, wash, repetat

    while True:

        # read from local_host
        local_buffer = receive_from(client_socket)

        if len(local_buffer):

            print "[==>] Received %d bytes from localhost." % len(local_buffer)
            hexdump(local_buffer)

            # send it to our request handler
            local_buffer = request_handler(local_buffer, remote_host)

            # send off the data to the remote host
            remote_socket.send(local_buffer)
            print "[==>] Sent to remote."

            # receive back the response
            remote_buffer = receive_from(remote_socket)

            if len(remote_buffer):

                print "[<==] Received %d bytes from remote." % len(remote_buffer)
                hexdump(remote_buffer)

                # send to our response handler
                remote_buffer = response_handler(remote_buffer)

                # send the response to the local socket
                client_socket.send(remote_buffer)

                print "[<==] Sent to local host"
            
            if not len(local_buffer) or not len(remote_buffer):
                client_socket.close()
                remote_socket.close()
                print "[*] No more data. Closing connections"

                break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except:
        print "[!!] Failed to listen on %s:%d" % (local_host, local_port)        
        print "[!!] Check for other listening sockets or correct permissions"
        sys.exit(0)

    print "[*] Listening on %s:%d" % (local_host, local_port)

    server.listen(5)

    try:
        while True:
            client_socket, addr = server.accept()

            # print out the local connection information
            print "[==>] Received incoming connection from %s:%d" % (addr[0], addr[1])

            # starts a thread to talk to the remote host
            proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first,))

            proxy_thread.start()
    except KeyboardInterrupt:
        print('interrupted!')
        os._exit(0)


def main():
    
    if len(sys.argv[1:]) != 5:
        print "Usage ./proxy.py [local_host] [local_port] [remote_host] [remote_port] [receive_first]"
        print "Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True"
        sys.exit(0)

    # setup local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # setup remote target
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    # this tells our proxy to connect and receive data
    # before sending to the remote host
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    # now sping up our listening socket
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

main()
    
