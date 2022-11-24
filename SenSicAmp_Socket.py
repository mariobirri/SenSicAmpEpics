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
import re
import numpy as np

remote_ip = "129.129.130.210" # should match the instrument IP address
port = 3000 # the port number of the instrument service
pattern = re.compile(r'[-+]?\d*\.\d+|\d+')

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
        s.connect((data.ip, data.port))
    except socket.error:
        print('failed to connect to ip ' + remote_ip)
    return s

# Socket send command
#--------------------
def SocketSend(Sock, cmd):
    try:
        # Send cmd string
        Sock.sendall(cmd)
        time.sleep(0.1)
    except socket.error:
        #Send failed
        print('Send failed')
        sys.exit()
        
# Socket receive command
#--------------------
def SocketRec(Sock, cmd):
    try:
        # Send cmd string
        Sock.sendall(cmd)
        # and wait
        time.sleep(0.1)
    except socket.error:
        #Send failed
        print('Send failed')
        sys.exit()
    msg = Sock.recv(4*4096)
    #print(reply)
    return msg


# Socket close
#--------------
def SocketClose(Sock):
    #close the socket
    Sock.close()
    print('Socket closed')
    time.sleep(1)
    sys.exit()
    
# transform String to data    
#-----------------------------------------

def getDataFromString(inString):
    if len(inString) > 0: 
        # Compile a pattern to capture float values
        returnValues = [float(i) for i in pattern.findall(str(inString))]
        return returnValues
    else:
        return -1

# place the right values into the right array   
# ------------------------------------------- 
def getAllValsFromData(inDataMatrix):
    ch1=[]; ch2=[]; ch3=[]; ch4=[];
    for i in range(0, len(inDataMatrix), 5):
        ch1.append(inDataMatrix[i+1])
        ch2.append(inDataMatrix[i+2])
        ch3.append(inDataMatrix[i+3])
        ch4.append(inDataMatrix[i+4])
    returnArray = [ch1, ch2, ch3, ch4]
    return returnArray


# calc mean values
# ------------------------------------------- 
def getMean(inDataMatrix):
    value = np.mean(inDataMatrix, dtype = np.float64)
    return value
            
#----------------------------------

s = SocketConnect()
SocketSend(s, data.startAmp)
SocketRec(s, data.setGain)
mean1 = 0.0
mean2 = 0.0
mean3 = 0.0
mean4 = 0.0
meanSum = 0.0
while True:
    currentString = SocketRec(s, data.getCurrentString)
    currentData = getDataFromString(currentString)
    data.currents = getAllValsFromData(currentData)
    mean1 = getMean(data.currents[0])
    mean2 = getMean(data.currents[1])
    mean3 = getMean(data.currents[2])
    mean4 = getMean(data.currents[3])
    meanSum = mean1 + mean2 + mean3 + mean4

SocketClose(s)

