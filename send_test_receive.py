#!/usr/bin/env python3
# Script to test sending a packet
# By krissma

#from __future__ import print_function, unicode_literals

from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint
import argparse
from btlejack.link import DeviceError
from btlejack.helpers import *
from btlejack.ui import CLIAdvertisementsSniffer, ForcedTermination, CLISendTestPacket, CLIReceiveTestPacket
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
# "\xaa\xaa\xaa\xaa"


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
    global sniffer
    global target_pattern

    # Start sending
    # device eventuell angeben mit devices=[comports()[0]])???
    """
    try:
        print(f"Sending")
        sender = CLISendTestPacket(verbose=True)
        print("initiated sender")
        print("Test2")
    except DeviceError as error:
        print('Error 1: Please connect a compatible Micro:Bit in order to use BtleJack for jamming')
        exit(-1)

    """

    if (target_pattern is not None):
        print("Target pattern: ", target_pattern)
        target_pattern = target_pattern.encode()
        print("Target_pattern.encode(): ", target_pattern)

    out = PatternMatcher(pattern=target_pattern)
    #print("This is out: ", out)
    # start sniffer for pattern detection
    i = 1
    try:
        sniffer = CLIAdvertisementsSniffer(
            verbose=True, channel=60, output=None, policy={"policy_type": "blacklist", "rules": []}, accept_invalid_crc=True, no_stdout=True)
    except DeviceError as error:
        print(
            'Error: Please connect a compatible Micro:Bit in order to use BtleJack for jamming')
        exit(-1)
    # TODO: brauche ich sniffing_packet_processing()?
    sniffing_packet_processing()


def sniffing_packet_processing():

    global sniffing
    global sniffer

    while sniffing:
        sniffer_mutex.acquire()
        sniffer.process_packets()
        sniffer_mutex.release()
        time.sleep(SLEEP_TIME_BETWEEN_PACKET_PROCESSING)

    sniffer.disable_adv_sniffing()


if __name__ == "__main__":
    main()
