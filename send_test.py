#!/usr/bin/env python3
# Script to test sending a packet
# By krissma

# from __future__ import print_function, unicode_literals



from pprint import pprint
import argparse
from btlejack.link import DeviceError
from btlejack.helpers import *
from btlejack.ui import CLIAdvertisementsSniffer, ForcedTermination, CLISendTestPacket
from binascii import hexlify, unhexlify
from serial.tools.list_ports import comports
import signal
import re
import time
import threading
import select
import subprocess
import os
import sys
BTLEJACK_SOURCE_PATH = "btlejack/"
DISCOVERY_BINARY = "discovery/discovery"
SCAN_TIMEOUT_SECONDS = 7
PATTERN_POSITION_MAC = 2


sys.path.insert(1, BTLEJACK_SOURCE_PATH)


# Dialog menu imports


# Globals
sender = None
sniffer = None
sniffing = True
sniffer_mutex = threading.Lock()
pattern_position = None
target_pattern = ""

# Helper functions


class PatternMatcher:
    def __init__(self, pattern=None):
        self.pattern = pattern

    def write_packet(self, a, b, c, packet):

        global sniffing
        global pattern_position
        global current_target_addr

        pos = packet.find(self.pattern)
        if pos != -1:
            pattern_position = pos - 10
            sniffing = False
            print(packet)
            current_target_addr = ':'.join(
                ["%02x" % i for i in reversed(packet[12:18])])
            print(current_target_addr)


def main():
    """ Main routine """

    global sender
    global counter
    SLEEP_TIME_BETWEEN_PACKET_PROCESSING = 1.25
 
    # mode 00 is original btlejack mode, mode 01 is modified BT LE mode, mode 02 is BT Classic mode 
    mode = 0x02
    channel = 5
    counter = 0

    #packet = bytes([mode, channel, 0xAA, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11,
                    #0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0xAA])

    #packet = bytes([mode, channel, 0xAA, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 
                    #0x11, 0x11, 0x11, 0x11, 0xAA])
    
    #packet = bytes([mode, channel, 0xAA, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11])

    #packet = bytes([mode, channel, 0xAA, 0x11, 0x11, 0x11, 0x11, 0x11, 0x09, 0x4d, 0x6f, 0x74,
                   # 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0xAA,
                   # 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0xAA,
                   # 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0xAA,
                   # 0x11, 0x11, 0x11, 0x11, 0x11, 0x11])


    packet = bytes([mode, channel, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55,
                    0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55,
                    0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55,
                    0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55,
                    0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55])

    # Start sending
    # device eventuell angeben mit devices=[comports()[0]])???
    try:
        print(f"Sending")
        sender = CLISendTestPacket(verbose=True, channel=5, payload=packet)
        print("initiated sender")
    except DeviceError as error:
        print(
            'Error: Please connect a compatible Micro:Bit in order to use BtleJack for jamming')
        exit(-1)

    
    while (True):
        #if (counter != 0 and counter % 8 == 0):
            #SLEEP_TIME_BETWEEN_PACKET_PROCESSING -= 0.001
            #print("New sleep time: {} at packet {} ".format(SLEEP_TIME_BETWEEN_PACKET_PROCESSING, counter))
        sender.send_test_packet(packet)
        counter += 1
        print("Sent %d packets" %(counter+2))
        time.sleep(SLEEP_TIME_BETWEEN_PACKET_PROCESSING)
    print("Sent %d packets" %(counter+2))




if __name__ == "__main__":
    main()
