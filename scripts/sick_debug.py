#!/usr/bin/env python

# Copyright 2016 Fetch Robotics Inc.
# Author: Derek King

from __future__ import print_function

import socket
import sys
import time

class SickDebug:
    def __init__(self, ip, port=2112):
        self.buf = ''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect( (ip, port) )
        self.sock.settimeout(1.0)

        # tell device to stop streaming
        #self.send("sMN MIStopIn")

        # tell device to stop streaming
        self.send("sRN LMDscandata")
        time.sleep(0.1)
        self.flush()

        resp = self.recv()
        print(resp)

    def flush(self):
        # flush kernel buffer into local buffer (self.buf)
        try:
            recv = self.sock.recv(1000)
            while len(recv):
                self.buf += recv
                recv = self.sock.recv(1000)
        except socket.timeout:
            pass
        # print out local buffer that will be flushed (for debugging)
        if len(self.buf):
            print("Flushed:", self.prettyMsg(self.buf))
        # now empty local buffer
        self.buf = str()


    def expect(self, send_msg, expected_resp_msg):
        """ Sends msg, and check response against expected value """
        self.send(send_msg)
        resp = self.recv()
        if resp != expected_resp_msg:
            raise RuntimeError("Expected %s, got %s'" % (expected_resp_msg, resp))


    def send(self, msg):
        """ Sends messages to device, will append <STX> and <ETX> to message """
        self.sock.sendall(chr(2)+msg+chr(3))


    def recv(self, timeout = 0.5):
        """ Received respose, will strip <STX> and <ETX> from response message """
        buf = self.buf
        while buf.find(chr(3)) < 0:
            buf += self.sock.recv(1000)

        start_idx = buf.find(chr(2))
        if start_idx < 0:
            print(" Could not find STX in buffer :", self.prettyMsg(buf))
        elif start_idx != 0:
            print(" Garbage data before STX :", self.prettyMsg(buf[:start_idx+1]))

        stop_idx = buf.find(chr(3))

        # Store any following messages in buffer
        self.buf = buf[stop_idx+1:]

        # Make sure remaining message has a STX at begining
        if len(self.buf) and (self.buf[0] != chr(2)):
            print(" Extra garbage after ETX :", self.prettyMsg(buf[stop_idx+1:]))

        if start_idx > stop_idx:
            print(" Found stop before start", start_idx, stop_idx)

        return buf[start_idx+1:stop_idx]


    @staticmethod
    def prettyMsg(msg):
        """ Returns message where chr(2) and chr(3) are replaced with <STX> and <ETX>"""
        lookup = {chr(2):'<STX>', chr(3):'<ETX>'}
        return str().join([ (lookup[c] if c in lookup else c) for c in msg ])


def main():
    if len(sys.argv) < 2:
        print("Usage: sick_deubg.py <ip_address>")
        print("Example: sick_debug.py 10.42.42.24")
        sys.exit(1)
    ip = sys.argv[1]
    sick = SickDebug(ip)
    sick.run()

if __name__ == '__main__':
    main()
