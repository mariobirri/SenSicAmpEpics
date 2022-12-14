# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 09:56:41 2022

@author: birri_m
"""

import time


# global strings
ip1 = 129
ip2 = 129
ip3 = 130
ip4 = 210
port = 3000

connect = 0
connected = 0
failedCon = 0
samples = 200


startAmp = b'setdac:32767'
setGain = b'setgainmode:8;4;2;2'
getCurrentString = b'startacqf:' + str(int(samples)).encode() 

#bias
getBiasState = b'biasstatus'
biasState = 'init'
biasValue = 0.0
biasOn = 0
setBias = b'setdac:'
setBiasOn = b'biason:'
setBiasOff = b'biasoff:'

#ch1, ch2 .. sum
currents = [[]]

mean1 = 0.0
mean2 = 0.0
mean3 = 0.0
mean4 = 0.0
meanSum = 0.0

kx  = 1.0
ky= 1.0
