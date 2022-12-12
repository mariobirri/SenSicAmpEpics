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
        data.conState = 'Socket connected'
    except socket.error:
        data.conState = 'Failed to create socket.'
        #sys.exit()
    try:
	ip = str(int(data.ip1)) + '.' + str(int(data.ip2)) + '.' + str(int(data.ip3)) + '.' + str(int(data.ip4))
        #Connect to remote server
        s.connect((ip, data.port))
	data.connected = 1
    except socket.error:
        data.conState = 'failed to connect to ip ' + ip
	data.connected = 0
	time.sleep(1)
    print(data.conState)
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
        data.conState = 'Send failed'
	print(data.conState)


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
        data.conState = 'Send failed'

    msg = Sock.recv(len)
    return msg


# Socket close
#--------------
def SocketClose(Sock):
    #close the socket
    Sock.close()
    data.conState = 'Socket closed'
    data.connected = 0
    print(data.conState)


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

# init amplifier
#-------------------------------------------
def init():
    while True:
        if data.connect == 1 and data.connected == 0:
                s = SocketConnect()
                break
        else:
                time.sleep(0.2)

    SocketSend(s, data.startAmp)
    SocketSend(s, data.setBiasOff)
    SocketRec(s, data.setGain, 1024)
    return s


# main function
#----------------------------------
def main():

    s = init()
    bias = data.biasValue
    biasOn = 0
    while True:


	if data.connect == 0 and data.connected == 1 and s != None:
		SocketClose(s)
	if data.connect == 1 and data.connected == 0:
		s = init()

	if data.connected == 1:
        	currentString = SocketRec(s, data.getCurrentString, 16384)
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
			data.biasOn = 1

        	if biasOn != data.biasOn:
                	if data.biasOn == 1:
				SocketSend(s, data.setBiasOn)
			else:
				SocketSend(s, data.setBiasOff)
                	biasOn = data.biasOn


if __name__ == '__main__':
    main()
