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
from btlejack.ui import CLIAdvertisementsSniffer, ForcedTermination, CLISendTestPacket, CLIAdvertisementsJammer
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
SLEEP_TIME_BETWEEN_PACKET_PROCESSING = 0.1
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

        global sniffing
        global pattern_position
        global current_target_addr

        pos = packet.find(self.pattern)
        if pos != -1:
            pattern_position = pos - 10
            sniffing = False
            print("Packet in pattern matcher: ", packet)
            #current_target_addr = ':'.join(
               # ["%02x" % i for i in reversed(packet[12:18])])
            print(current_target_addr)

def jamming_packet_processing():

    global jammer

    while(True):
        jammer_mutex.acquire()
        jammer.process_packets()
        jammer_mutex.release()
        time.sleep(SLEEP_TIME_BETWEEN_PACKET_PROCESSING)


def main():
    """ Main routine """

    global jammer
    global current_target_addr 
    global target_pattern 
    global pattern_position
    global jammer_mutex 
    #TODO what is pattern position?


    # mode 00 is original btlejack mode, mode 01 is modified BT LE mode, mode 02 is BT Classic mode 
    mode = 0x02; 

    #current_target_addr = "094d6f74"
    current_target_addr = "FFAC123D"
    target_pattern = bytes.fromhex(current_target_addr)
    pattern_position = 0
    
    jammer_mutex = threading.Lock()

  
    print(f"Jamming all advertisements of {current_target_addr}")
    # time.sleep(1)

    # Start jammer
    try:
        print(f"jamming {target_pattern} at {pattern_position}")
        jammer = CLIAdvertisementsJammer(verbose=False, channel = 5, mode=mode, pattern=target_pattern, position=pattern_position)
    except DeviceError as error:
        print('Error: Please connect a compatible Micro:Bit in order to use BtleJack for jamming')
        exit(-1)

    # Start jammer background process
    jammer_process = threading.Thread(target=jamming_packet_processing)
    jammer_process.start()



if __name__ == "__main__":
    main()
