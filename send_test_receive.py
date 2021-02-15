#!/usr/bin/env python3
# Script to test sending a packet
# By krissma

#from __future__ import print_function, unicode_literals

#from examples import custom_style_2
from PyInquirer import style_from_dict, Token, prompt, Separator
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
import signal
import re
import time
import threading
import select
import sys
import datetime  
import btlejack.supervisors
BTLEJACK_SOURCE_PATH = "btlejack/"
DISCOVERY_BINARY = "discovery/discovery"
SCAN_TIMEOUT_SECONDS = 7
SLEEP_TIME_BETWEEN_PACKET_PROCESSING = 0.01
PATTERN_POSITION_MAC = 2


sys.path.insert(1, BTLEJACK_SOURCE_PATH)


# Dialog menu imports


# Globals
sender = None
sniffer = None
sniffing = True
sniffer_mutex = threading.Lock()
pattern_position = None
target_pattern = None


# Helper functions


class PatternMatcher:
    def __init__(self, pattern=None):
        self.pattern = pattern

    def write_packet(self, a, b, c, packet):
        #print("in write_packet")
        global sniffing
        global pattern_position
        global current_target_addr

        #print("Packet in pattern matcher: ", packet)
        current_target_addr = ':'.join(["%02x" % i for i in (packet[12:18])])
        #print("Target address: ", current_target_addr)

        pos = packet.find(self.pattern)
        if pos != -1:
            pattern_position = pos - 10
            sniffing = False
            print("Packet in pattern matcher: ", packet)
            #current_target_addr = ':'.join(
               # ["%02x" % i for i in reversed(packet[12:18])])
            print(current_target_addr)


def main():
    """ Main routine """

    global sender
    global sniffer
    global target_pattern
    global target_pattern

    # mode 00 is original btlejack mode, mode 01 is modified BT LE mode, mode 02 is BT Classic mode 
    mode = 0x01; 
   
    current_target_addr = "FFAC123D"
    target_pattern = bytes.fromhex(current_target_addr)

    # example packet for test method, can be compared with packet transmitted by send_test.py
    sentPacket = bytes([0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55,
                        0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55,
                        0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55,
                        0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55,
                        0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55])

    # Start sending
    out = PatternMatcher(pattern = target_pattern)
    
    # start sniffer for pattern detection
    try:
        sniffer = CLIAdvertisementsSniffer(
            verbose=True, channel=37, mode=mode, pattern=target_pattern,
            output=out, policy={"policy_type": "blacklist", "rules": []}, accept_invalid_crc=True, no_stdout=True)
    except DeviceError as error:
        print(
            'Error: Please connect a compatible Micro:Bit in order to use BtleJack for jamming')
        exit(-1)
    sniffing_packet_processing(sentPacket)


def sniffing_packet_processing(sentPacket):

    global sniffing
    global sniffer
    global counter_jammed
    global counter_no_jam
   
    
    counter_jammed = 0
    counter_no_jam = 0


    while sniffing:
        sniffer_mutex.acquire()
        sniffer.process_packets_receiver(sentPacket)
        sniffer_mutex.release()
        time.sleep(SLEEP_TIME_BETWEEN_PACKET_PROCESSING)

    sniffer.disable_adv_sniffing()



if __name__ == "__main__":
    main()
