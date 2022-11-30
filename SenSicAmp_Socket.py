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
        print('failed to connect to ip ' + data.ip)
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
def SocketRec(Sock, cmd, len):
    try:
        # Send cmd string
        Sock.sendall(cmd)
        # and wait
        time.sleep(0.1)
    except socket.error:
        #Send failed
        print('Send failed')
        sys.exit()
    msg = Sock.recv(len)
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

# main function
#----------------------------------
def main():
    s = SocketConnect()
    SocketSend(s, data.startAmp)
    SocketRec(s, data.setGain, 1024)
    bias = data.biasValue
    biasOn = data.biasOn

    while True:
        currentString = SocketRec(s, data.getCurrentString, 4096*4)
        currentData = getDataFromString(currentString)
        currents = getAllValsFromData(currentData)
        data.mean1 = getMean(currents[0])
        data.mean2 = getMean(currents[1])
        data.mean3 = getMean(currents[2])
        data.mean4 = getMean(currents[3])
        data.meanSum = data.mean1 + data.mean2 + data.mean3 + data.mean4
	data.biasState = SocketRec(s, data.getBiasState, 1024)
	if bias != data.biasValue:
		sendValue = data.setBias+str(int(((data.biasValue+21)/42)*65535)).encode()
		SocketSend(s, sendValue)
		bias = data.biasValue
		print(sendValue)
		print(bias)
        if biasOn != data.biasOn:
                if data.biasOn == 1:
			SocketSend(s, data.setBiasOff)
		else:
			SocketSend(s, data.setBiasOn)
                biasOn = data.biasOn
                print(data.biasOn)

    SocketClose(s)


if __name__ == '__main__':
    main()
