#!/usr/bin/env python

import socket
import paramiko
import threading
import sys

# using the key from the Paramiko demo files
host_key = paramiko.RSAKey(filename='test_rsa.key')

class Server (paramiko.ServerInterface):
    def _init_(self):
        self.event = threading.Event()

    def set_username_password(self, username, password):
        self.username = username
        self.password = password

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == self.username) and (password == self.password):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

if len(sys.argv[1:]) != 4:
        print "Usage ./nc_sshServer.py [ip] [port] [username] [password]"
        print "Example: ./nc_sshServer.py 192.168.0.10 2222 user p@ssw0rd1"
        sys.exit(0)

server = sys.argv[1]
ssh_port = int(sys.argv[2])
username = sys.argv[3]
password = sys.argv[4]

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print '[+] Listening for connection...'
    client, addr = sock.accept()
except Exception, e:
    print '[-] Listen failed: ' + str(e)
    sys.exit(1)

print '[+] Got a connection!'

try:
    nc_session = paramiko.Transport(client)
    nc_session.add_server_key(host_key)
    server = Server()
    server.set_username_password(username, password)

    try:
        nc_session.start_server(server=server)
    except paramiko.SSHException, x:
        print '[-] SSH negotiation failed.'
    except Exception, e:
        print '[-] Caught exception: when startin server ' + str(e)

    chan = nc_session.accept(20)
    print '[+] Authenticated!' 
    print chan.recv(1024)
    chan.send('Welcome to nc_ssh')

    while True:
        try:
            command= raw_input("Enter command: ").strip('\n')
            if command != 'exit':
                chan.send(command)
                print chan.recv(1024) + '\n'
            else:
                chan.send('exit')
                print 'exiting'
                nc_session.close()
                raise Exception ('exit')
        except KeyboardInterrupt:
            nc_session.close()
except Exception, e:
    print '[-] Caught exception: ' + str(e)
    try:
        nc_session.close()
    except:
        pass
    sys.exit(1)



