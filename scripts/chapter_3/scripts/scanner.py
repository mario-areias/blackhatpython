#!/usr/bin/env python

import socket
import os
import struct
import threading
import time
import getopt
import datetime
import sys
from netaddr import IPNetwork,IPAddress
from ctypes import *

DEFAULT_MESSAGE = "PENTESTERHERE!"
magic_message = DEFAULT_MESSAGE
verbose = False
filename = None
output_file = None

def usage():
    print "Scanner tool"
    print
    print "Attention: It requires sudo privileges in order to get the network card in promiscuous mode"
    print "Usage: scanner.py -t target_host -s subnet -m magic_message -o file"
    print "-t --target    - target host to listen for ICMP packages (usually the IP where the scanner is running)"
    print "-s --subnet    - subnet to be scanned"
    print "-m --message   - magic message to identify the correct packages. Default: %s" % DEFAULT_MESSAGE
    print "-f --file      - stores output in a file (it also prints on stdout)"
    print "-v --verbose   - to enable more logs"
    print "-h --help      - to display this message"
    print
    print
    print "Examples: "
    print "scanner.py -t 192.168.0.1 -s '192.168.0.0/24' -m MAGIC -v"
    print "scanner.py -t 192.168.0.1 -s '192.168.0.0/24' -m MAGIC -v -f test"
    sys.exit(0)

if not len(sys.argv[1:]):
    usage()

# read the commandline options 
try:
    opts, args = getopt.getopt(sys.argv[1:],"t:s:m:f:vh", 
        ["target","subnet","message","file","verbose","help"])
except getopt.GetoptError as err:
    print str(err)
    usage()

for o,a in opts:
    if o in ("-h","--help"):
        usage()
    elif o in ("-t", "--target"):
        host = a
    elif o in ("-s", "--subnet"):
        subnet = a
    elif o in ("-m", "--message"):
        magic_message = a
    elif o in ("-f", "--file"):
        filename = a
    elif o in ("-v","--verbose"):
        verbose = True
    else:
        print o
        assert False, "Unhandled Option"

if filename:
    currentDT = datetime.datetime.now()

    output_file = open(filename, 'a')
    output_file.write('### Begin scan for subnet %s on %s \n' % (subnet, currentDT.strftime("%Y-%m-%d %H:%M:%S")))

def print_verbose_message(message):
    if verbose: print message
    if verbose and output_file: output_file.write('%s \n' % message)

def print_message(message):
    print message
    if output_file: output_file.write('%s \n' % message)

def udp_sender(subnet, magic_message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ip in IPNetwork(subnet):
        try:
            sender.sendto(magic_message, ("%s" % ip, 65212))
        except:
            pass

# our IP header
class IP(Structure):
    _fields_ = [
        ("ihl",          c_ubyte, 4),
        ("version",      c_ubyte, 4),
        ("tos",          c_ubyte),
        ("len",          c_ushort),
        ("id",           c_ushort),
        ("offset",       c_ushort),
        ("ttl",          c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum",          c_ushort),
        ("src",          c_uint32),
        ("dst",          c_uint32)
    ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)
    
    def __init__(self, socket_buffer=None):

        # map protocol constants to their names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # human readable IP address
        self.src_address = socket.inet_ntoa(struct.pack("@I",self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I",self.dst))

        # human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

class ICMP(Structure):

    _fields_ = [
        ("type", c_ubyte),
        ("code", c_ubyte),
        ("checksum", c_ushort),
        ("unused", c_ushort),
        ("next_hop_mtu", c_ushort)
    ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)
    
    def __init__(self, socket_buffer):
        pass

# create a row socket and bind it to the public interface
if os.name == 'nt':
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))

# We want the IP headers included in the capture
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# if we are using Windows we need to send an IOCTL
# to set up promismicious mode
if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# start sending packets
t = threading.Thread(target=udp_sender, args=(subnet, magic_message))
t.start()

try:

    while True:
        # read in a packet
        raw_buffer = sniffer.recvfrom(65565)[0]

        # create an IP header from the buffer
        ip_header = IP(raw_buffer)
        print_verbose_message("Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))    

        # if it is ICMP, we want it
        if ip_header.protocol == "ICMP":

            # calculate where our ICMP packet starts
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset: offset + sizeof(ICMP)]

            # create our ICMP structure
            icmp_header = ICMP(buf)
            print_verbose_message("ICMP -> Type: %d Code: %d" % (icmp_header.type, icmp_header.code))

            # now check for the TYPE 3 and CODE
            if icmp_header.code == 3 and icmp_header.type == 3:
                
                # make sure host is in our target subnet
                if IPAddress(ip_header.src_address) in IPNetwork(subnet):

                    # make sure it has our magic message
                    if raw_buffer[len(raw_buffer) - len(magic_message):] == magic_message:
                        print_message("Host up: %s" % ip_header.src_address)
                        
# handle CTRL-C
except KeyboardInterrupt:
    if output_file:
        output_file.write('### End scan \n\n')
        output_file.close()

    # if we're using Windows, turn off promiscuous mode
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

