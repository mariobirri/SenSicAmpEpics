#!/usr/bin/env python
from pcaspy import Driver, SimpleServer
import SenSicAmp_data as data

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


class myDriver(Driver):
    global meanValues,s,p
    #print(getMeanCurrent(getData(s),p))
    def  __init__(self):
        super(myDriver, self).__init__()

    def read(self, reason):
	#print(getMeanCurrent(getData(s),p))
        if reason == 'CUR1': value = data.mean1
        elif reason == 'CUR2': value = data.mean2 
        elif reason == 'CUR3': value = data.mean3 
        elif reason == 'CUR4': value = data.mean4
        elif reason == 'SUM':  value = data.meanSum
        elif reason == 'POSX': value = 0
        elif reason == 'POSY': value = 0
        elif reason == 'BIASSTATE': 0
        else:
            value = self.getParam(reason)
        return value


    def write(self, reason, value):
        status = True

        if reason == 'BIAS':
            print('new bias voltage = %x' % value)
        if status:
           self.setParam(reason, value)

        return status

if __name__ == '__main__':
    server = SimpleServer()
    server.createPV(prefix, pvdb)
    driver = myDriver()

    # process CA transactions
    while True:
	    server.process(0.5)

