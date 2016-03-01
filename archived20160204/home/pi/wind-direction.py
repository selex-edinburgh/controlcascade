# Wind Direction
# Connect black wire from wind vane to ground
# Connect green wire from wind vane to A0 on ADS1015 board
# Connect a 10K resistor from the green wire to +3.3V
# (the voltages below will need to be changed if you use +5V instead)

import time
from Adafruit_ADS1x15 import *

adc = ADS1x15()

gain = 4096
sps = 250

while (True):
    volts = adc.readADCSingleEnded(0) / 1000
    # print "voltage: %.3f" % volts
    if (volts < 0.45):
        print "W"
    elif (volts < 0.9):
        print "NW"
    elif (volts < 1.35):
        print "N"
    elif (volts < 1.75):
        print "SW"
    elif (volts < 2.25):
        print "NE"
    elif (volts < 2.70):
        print "S"
    elif (volts < 2.95):
        print "SE"
    elif (volts < 3.2):
        print "E"
    else:
        print "unknown"
