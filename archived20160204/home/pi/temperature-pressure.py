# Temperature and Pressure

from Adafruit_BMP085 import BMP085

tempchip = BMP085(0x77)

temp = tempchip.readTemperature()
pressure = tempchip.readPressure()

print "The temperature is %.2f C" % temp

print "The pressure is %.2f Pa" % pressure

# convert pressure from Pascals to Millibar
# 1 mbar = 1 hPA = 100Pa.

print "The pressure is %.2f mbar" % (pressure / 100)
