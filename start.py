import os
from multiprocessing import Process

path = "/home/pi/SenSicAmpEpics/"
tasks = ['SenSicAmp_epics.py', 'SenSicAmp_Socket.py']

def foo(task):
    os.system('python ' + path + task)

for task in tasks:
    p = Process(target=foo, args=(task,))
    p.start()
