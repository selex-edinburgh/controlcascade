# Light Dependent Resistor

import time
from Adafruit_ADS1x15 import *

adc = ADS1x15()

gain = 4096
sps = 250

while (True):
    volts = adc.readADCSingleEnded(0) / 1000
    print "voltage: %.3f" % volts
