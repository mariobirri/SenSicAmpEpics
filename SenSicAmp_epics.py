#!/usr/bin/env python
from pcaspy import Driver, SimpleServer
import SenSicAmp_data as data 
import SenSicAmp_Socket

import threading

#Epics Stuff
prefix = 'X05LA-ES-SENSIC:'
pvdb = {
    'POSX' :		{'TYPE' : 'int', 'scan' : 0.1, 'unit' : 'um', 'prec' : 10 },
    'POSY' :		{'TYPE' : 'int', 'scan' : 0.1, 'unit' : 'um', 'prec' : 10 },
    'CUR1' :		{'TYPE' : 'int', 'scan' : 0.1, 'unit' : 'A', 'prec' : 10 },
    'CUR2' :		{'TYPE'	: 'int', 'scan' : 0.1, 'unit' : 'A', 'prec' : 10 },
    'CUR3' :		{'TYPE' : 'int', 'scan' : 0.1, 'unit' : 'A', 'prec' : 10},
    'CUR4' :		{'TYPE' : 'int', 'scan' : 0.1, 'unit' : 'A', 'prec' : 10},
    'SUM'  :		{'TYPE' : 'int', 'scan' : 0.1, 'unit' : 'A', 'prec' : 10},
    'BIAS'  :   	{'TYPE' : 'int', 'scan' : 0.5, 'unit' : 'V', 'prec' : 2},
    'BIASON'  :   	{'TYPE' : 'int', 'scan' : 0.5, 'unit' : ' ', 'prec' : 0},
    'BIASSTATE'  :   	{'TYPE' : 'char','scan' : 0.5, 'count' : 10},
    'KX'  :		{'TYPE' : 'int', 'scan' : 0.5, 'unit' : ' ', 'prec' : 2},
    'KY'  :		{'TYPE' : 'int', 'scan' : 0.5, 'unit' : ' ', 'prec' : 2},
    'NUMTOMEAN'  :     	{'TYPE' : 'int', 'unit' : ' ', 'prec' : 0},
}

def getPosX(valueArr):
    if valueArr[4] != 0:
        return data.kx*(((valueArr[0] + valueArr[2])-(valueArr[1] + valueArr[3]))/valueArr[4])
    else:
        return 0
 
def getPosY(valueArr):
    if valueArr[4] != 0:
        return data.ky*(((valueArr[0] + valueArr[1])-(valueArr[2] + valueArr[3]))/valueArr[4])
    else:
        return 0


class myDriver(Driver):
    global data
    def  __init__(self):
        super(myDriver, self).__init__()
        # start the communication socket
        t = threading.Thread(target=SenSicAmp_Socket.main)
	# change T to daemon
	t.setDaemon(True)
	t.start()

    def read(self, reason):
        if reason == 'CUR1': value = data.mean1
        elif reason == 'CUR2': value = data.mean2
        elif reason == 'CUR3': value = data.mean3
        elif reason == 'CUR4': value = data.mean4
        elif reason == 'SUM':  value = data.meanSum
        elif reason == 'POSX': value = getPosX([data.mean1, data.mean2, data.mean3, data.mean4, data.meanSum])
        elif reason == 'POSY': value = getPosY([data.mean1, data.mean2, data.mean3, data.mean4, data.meanSum])
        elif reason == 'KX': value = data.kx
        elif reason == 'KY': value = data.ky
        elif reason == 'BIASSTATE': value = data.biasState
        elif reason == 'BIAS': value = data.biasValue
        elif reason == 'BIASON': value = data.biasOn
	else: value = self.getParam(reason)
        return value


    def write(self, reason, value):
        status = True

        if reason == 'KX': data.kx = value
        elif reason == 'KY': data.ky = value
	elif reason == 'BIAS': data.biasValue = value
	elif reason == 'BIASON': data.biasOn = value
        if status:
           self.setParam(reason, value)

        return status

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
        server.process(0.1)

