#!/usr/bin/env python

import sys
import threading
import paramiko
import subprocess


def ssh_command(ip, user, passwd, port, command):
    client = paramiko.SSHClient()
    
    # client.load_host_keys("~/.ssh/known_hosts")
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=passwd, port=port)
    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
        ssh_session.exec_command(command)
        print ssh_session.recv(1024)
    return

def main():
    if len(sys.argv[1:]) != 5:
        print "Usage ./nc_sshcmd.py [ip] [user] [password] [sshPort] [command]"
        print "Example: ./nc_sshcmd.py 192.168.0.10 2222 user p@ssw0rd1 id"
        sys.exit(0)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    user = sys.argv[3]
    password = sys.argv[4]
    command = sys.argv[5]

    ssh_command(ip, user, password, port, command)


main()
