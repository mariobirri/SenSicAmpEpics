# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 09:56:41 2022

@author: birri_m
"""

#!/usr/bin/env python
import socket # for sockets
import SenSicAmp_data as data
import sys
import time

remote_ip = "129.129.130.210" # should match the instrument IP address
port = 3000 # the port number of the instrument service

# Socket connection
#-------------------
def SocketConnect():
    try:
        #create an AF_INET, STREAM socket (TCP)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket connected')
    except socket.error:
        print('Failed to create socket.')
        sys.exit()
    try:
        #Connect to remote server
        s.connect((remote_ip, port))
    except socket.error:
        print('failed to connect to ip ' + remote_ip)
    print('Communication success')
    return s

# Socket send command
#--------------------
def SocketQuery(Sock, cmd):
    try:
        # Send cmd string
        Sock.sendall(cmd)
        # and wait
        time.sleep(0.1)
    except socket.error:
        #Send failed
        print('Send failed')
        sys.exit()
    reply = Sock.recv(4096)
    #print(reply)
    return reply

# Socket close
#--------------
def SocketClose(Sock):
    #close the socket
    Sock.close()
    time.sleep(1)
#-------------------------------------------------------------------------

s = SocketConnect()
val = SocketQuery(s, data.startAmp)
print(val) 
time.sleep(1)
val = SocketQuery(s, data.setGain)
print(val)
SocketClose(s)

