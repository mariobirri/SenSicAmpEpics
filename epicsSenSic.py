#!/usr/bin/env python
from pcaspy import Driver, SimpleServer
import socket # for sockets
import time
import re
import sys

remote_ip = "129.129.130.210" # should match the instrument IP address
port = 3000 # the port number of the instrument service


#Epics Stuff
prefix = 'X05LA-ES-SENSIC:'
pvdb = {
    'POSX' :	{'TYPE' : 'int', 'scan' : 0.2, 'unit' : 'um', 'prec' : 10 },
    'POSY' :	{'TYPE' : 'int', 'scan' : 0.2, 'unit' : 'um', 'prec' : 10 },
    'CUR1' :	{'TYPE' : 'int', 'scan' : 0.2, 'unit' : 'A', 'prec' : 10 },
    'CUR2' :	{'TYPE'	: 'int', 'scan' : 0.2, 'unit' : 'A', 'prec' : 10 },
    'CUR3' :	{'TYPE' : 'int', 'scan' : 0.2, 'unit' : 'A', 'prec' : 10},
    'CUR4' :	{'TYPE' : 'int', 'scan' : 0.2, 'unit' : 'A', 'prec' : 10},
    'SUM'  :	{'TYPE' : 'int', 'scan' : 0.2, 'unit' : 'A', 'prec' : 10},
    'BIAS'  :   {'TYPE' : 'int',  'unit' : 'V', 'prec' : 2},
    'BIASON'  :   {'TYPE' : 'int', 'scan' : 0.2, 'unit' : ' ', 'prec' : 0},
    'BIASOFF'  :   {'TYPE' : 'int', 'scan' : 0.2, 'unit' : ' ', 'prec' : 0},
    'BIASSTATE'  :   {'TYPE' : 'char', 'count' : 10},
}

def SocketConnect():
    try:
        #create an AF_INET, STREAM socket (TCP)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print('Socket connected')
    except socket.error:
        print ('Failed to create socket.')
        sys.exit();
    try:
        #Connect to remote server
        s.connect((remote_ip , port))
    except socket.error:
        print ('failed to connect to ip ' + remote_ip)
    try:
	s.sendall(b'setdac:50')
	s.sendall(b'setgainmode:8;4;2;2')
    except socket.error:
	print ('Failed to init amplifier')
    try:
	s.sendall(b'readgainmode')
	time.sleep(0.05)
	print(s.recv(4096))
    except socket.error:
	print('No gain mode read')
    return s


def SocketQuery(Sock, cmd):
    try :
        #Send cmd string
        Sock.sendall(cmd)
        #Sock.sendall(b'\r\n')
        time.sleep(0.05)
    except socket.error:
        #Send failed
        print ('Send failed')
        sys.exit()
    reply = Sock.recv(4096)
    #print(reply)
    return reply

def SocketClose(Sock):
    #close the socket
    Sock.close()
    time.sleep(1)
#-------------------------------------------------------------------------

s = SocketConnect()
p = re.compile(r'[-+]?\d*\.\d+|\d+')
meanValues = [0,0,0,0,0]
pos = [0,0]

def getData(s):
	return str(SocketQuery(s, b'startacqf:1'))

def getMeanCurrent(dataString, p):
	global meanValues

	currMean = [0,0,0,0,0]

	# Compile a pattern to capture float values
	vals = [float(j) for j in p.findall(dataString)]  # Convert strings to float
	#print(vals)
	try:
       		#print(vals[k], vals[k+1], vals[k+2], vals[k+3], vals[k+4])
       		currMean[0] = vals[1]
       		currMean[1] = vals[2]
		currMean[2] = vals[3]
		currMean[3] = vals[4]
	except: 
		print('no entry')

	currMean[4] = currMean[0] + currMean[1] + currMean[2] + currMean[3]
	meanValues = currMean
	return meanValues

def getPos(index):
	global meanValues, pos
	if index == 0 and meanValues[4] != 0:
		pos[0] = ((meanValues[0]+meanValues[2])-(meanValues[1]+meanValues[3]))/meanValues[4]
		return pos[0]
	elif index == 1 and meanValues[4] != 0:
        	pos[1] = ((meanValues[0]+meanValues[1])-(meanValues[2]+meanValues[3]))/meanValues[4]
		return pos[1]
	else:
		return -1

class myDriver(Driver):
    global meanValues,s,p
    #print(getMeanCurrent(getData(s),p))
    def  __init__(self):
        super(myDriver, self).__init__()

    def read(self, reason):
	#print(getMeanCurrent(getData(s),p))
        if reason == 'CUR1': value = meanValues[0]
	elif reason == 'CUR2': value = meanValues[1] 
        elif reason == 'CUR3': value = meanValues[2] 
        elif reason == 'CUR4': value = meanValues[3]
        elif reason == 'SUM':  value = meanValues[4]
        elif reason == 'POSX': value = getPos(0)
        elif reason == 'POSY': value = getPos(1)
	elif reason == 'BIASSTATE': value = SocketQuery(s, b'biasstatus')
        else:
		value = self.getParam(reason)
        return value


    def write(self, reason, value):
        status = True

        if reason == 'BIAS':
           print 'new bias voltage = %x' % value
	   SocketQuery(s, b'setbias:' + str(value))

        if status:
           self.setParam(reason, value)

        return status

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
	print(getMeanCurrent(getData(s),p))
        server.process(0.5)

