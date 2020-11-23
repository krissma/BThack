#!/usr/bin/env python3
# Script to test sending a packet
# By krissma

# from __future__ import print_function, unicode_literals

from examples import custom_style_2
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
    global sniffer
    global target_pattern

    # Start sending
    # device eventuell angeben mit devices=[comports()[0]])???
    try:
        print(f"Sending")
        sender = CLISendTestPacket(verbose=True, channel=37)
        print("initiated sender")
    except DeviceError as error:
        print(
            'Error: Please connect a compatible Micro:Bit in order to use BtleJack for jamming')
        exit(-1)

    while(True):
        sender.send_test_packet()
        time.sleep(SLEEP_TIME_BETWEEN_PACKET_PROCESSING)

    """
    if (target_pattern is not None):
        print("Target pattern: ", target_pattern)
        target_pattern = target_pattern.encode()
        print("Target_pattern.encode(): ", target_pattern)


    out = PatternMatcher(pattern=target_pattern)
    # start sniffer for pattern detection
    try:
        sniffer = CLIAdvertisementsSniffer(
            verbose=True, output=out, no_stdout=True)
    except DeviceError as error:
        print('Error: Please connect a compatible Micro:Bit in order to use BtleJack for jamming')
        exit(-1)
    """
    # TODO: brauche ich sniffing_packet_processing()?


# sniffing_packet_processing()


def sniffing_packet_processing():

    global sniffing
    global sniffer

    while sniffing:
        sniffer_mutex.acquire()
        sniffer.process_packets()
        sniffer_mutex.release()
        time.sleep(SLEEP_TIME_BETWEEN_PACKET_PROCESSING)

    sniffer.disable_adv_sniffing()


# TODO adapt this for receiving a message? Do I actually need this?
"""

def search_target(scan_dev_num, target_pattern):

   Scans for nearby BLE devices and offers pattern matching on their names or menu selection

    while(True):
        print(f"Conducting BLE scan ({SCAN_TIMEOUT_SECONDS} seconds)")
        begin_line_counter = 0
        target_options = {}
        # Start BLE scan
        process = subprocess.Popen(
            [DISCOVERY_BINARY, str(scan_dev_num)], stdout=subprocess.PIPE)
        poll_obj = select.poll()
        poll_obj.register(process.stdout, select.POLLIN)
        timeout = time.time() + SCAN_TIMEOUT_SECONDS
        while True:

            # Stop process gracefuly after time-limit
            if(time.time() > timeout):
                process.send_signal(signal.SIGINT)

            # Abort if process died/killed
            return_code = process.poll()
            if return_code is not None:
                break

            # Check if data is available
            if(not poll_obj.poll(0)):
                continue

            # Check results to allow pattern matching
            result = process.stdout.readline()
            # Ugly hack to skip first lines of output
            if(begin_line_counter < 6):
                begin_line_counter += 1
                continue

            result = result.strip().decode().split(', ')

            try:
                result[0] = is_valid_mac(result[0])
            except(argparse.ArgumentTypeError):
                continue

            if len(result) == 3 and result[2] is not None and target_pattern is not None and target_pattern in result[2]:
                print(f"Found target: {result}")
                return result[0]
            if result[0] not in target_options or target_options[result[0]] is None:
                if(len(result) < 3):
                    target_options[result[0]] = None
                    continue
                target_options[result[0]] = result[2]

        if(target_options is not None):
            print("Could not identify target -> prompting alternatives")

"""

if __name__ == "__main__":
    main()
