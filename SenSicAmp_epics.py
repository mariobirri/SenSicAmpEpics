#!/usr/bin/env python
from pcaspy import Driver, SimpleServer
import SenSicAmp_data as data 

print(id(data))
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
    'BIASSTATE'  :   {'TYPE' : 'char', 'count' : 10},
    'KX'  :	{'TYPE' : 'int', 'scan' : 0.2, 'unit' : ' ', 'prec' : 2},
    'KY'  :	{'TYPE' : 'int', 'scan' : 0.2, 'unit' : ' ', 'prec' : 2},
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
        elif reason == 'BIASSTATE': value = ''
        else: value = self.getParam(reason)
        return value


    def write(self, reason, value):
        status = True

        if reason == 'KX': data.kx = value
        elif reason == 'KY': data.ky = value
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

