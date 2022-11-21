#!/usr/bin/env python
from pcaspy import Driver, SimpleServer
import socket # for sockets
import time
import re

remote_ip = "129.129.130.210" # should match the instrument IP address
port = 3000 # the port number of the instrument service


#Epics Stuff
prefix = 'X05LA-ES-SENSIC:'
pvdb = {
    'POSX' :	{'TYPE' : 'int', 'scan' : 0.1, 'unit' : 'um', 'prec' : 2 },
    'POSY' :	{'TYPE' : 'int', 'scan' : 0.1, 'unit' : 'um', 'prec' : 2 },
    'CUR1' :	{'TYPE' : 'int', 'scan' : 0.1, 'unit' : 'A', 'prec' : 10 },
    'CUR2' :	{'TYPE'	: 'int', 'scan' : 0.1, 'unit' : 'A', 'prec' : 10 },
    'CUR3' :	{'TYPE' : 'int', 'scan' : 0.1, 'unit' : 'A', 'prec' : 10},
    'CUR4' :	{'TYPE' : 'int', 'scan' : 0.1, 'unit' : 'A', 'prec' : 10},
    'SUM'  :	{'TYPE' : 'int', 'scan' : 0.1, 'unit' : 'A', 'prec' : 10},
}

def SocketConnect():
    try:
        #create an AF_INET, STREAM socket (TCP)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print ('Failed to create socket.')
        sys.exit();
    try:
        #Connect to remote server
        s.connect((remote_ip , port))
    except socket.error:
        print ('failed to connect to ip ' + remote_ip)
    return s

def SocketQuery(Sock, cmd):
    try :
        #Send cmd string
        Sock.sendall(cmd)
        #Sock.sendall(b'\n')
        time.sleep(0.1)
    except socket.error:
        #Send failed
        print ('Send failed')
        sys.exit()
    reply = Sock.recv(4096)
    return reply

def SocketClose(Sock):
    #close the socket
    Sock.close()
    time.sleep(1)
#-------------------------------------------------------------------------

s = SocketConnect()
p = re.compile(r'[-+]?\d*\.\d+|\d+')
meanValues = [0,0,0,0,0]

def getData(s):
	return str(SocketQuery(s, b'startacqc:50'))

def getMeanCurrent(dataString, p):
	global meanValues

	arr2 = []
	arr3 = []
	arr4 = []
	arr5 = []
	currMean = [0,0,0,0,0]

	# Compile a pattern to capture float values

	vals = [float(j) for j in p.findall(dataString)]  # Convert strings to float
	for k in range(0, len(vals), 5):
        	#print(vals[k], vals[k+1], vals[k+2], vals[k+3], vals[k+4])
        	arr2.append(vals[k+1])
        	arr3.append(vals[k+2])
        	arr4.append(vals[k+3])
        	arr5.append(vals[k+4])

	if len(arr2) > 0: currMean[0] = sum(arr2) / len(arr2)
	if len(arr3) > 0: currMean[1] = sum(arr3) / len(arr3)
	if len(arr4) > 0: currMean[2] = sum(arr4) / len(arr4)
	if len(arr5) > 0: currMean[3] = sum(arr5) / len(arr5)
	currMean[4] = currMean[0] + currMean[1] + currMean[2] + currMean[3]

	meanValues = currMean

class myDriver(Driver):
    global meanValues
    def  __init__(self):
        super(myDriver, self).__init__()

    def read(self, reason):
        if reason == 'CUR1': value = meanValues[0]
	elif reason == 'CUR2': value = meanValues[1]
        elif reason == 'CUR3': value = meanValues[2]
        elif reason == 'CUR4': value = meanValues[3]
        elif reason == 'SUM':  value = meanValues[4]
        elif reason == 'POSX': value = meanValues[0]
        elif reason == 'POSY': value = meanValues[0]
        else:
		value = self.getParam(reason)
	#print(value)
        return value


    def write(self, reason, value):
        status = True

        if reason == 'COLOR':
           print 'new color code is %x' % value

        if status:
           self.setParam(reason, value)

        return status

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
	getMeanCurrent(getData(s),p)
        server.process(0.1)

