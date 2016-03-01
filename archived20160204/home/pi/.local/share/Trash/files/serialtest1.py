import from serial serial
import time

port = serial.serial("/dev/ttyAMA0", baudrate = 9600, timeout = 3.0)

#while True:
#  port.write("\r\nSay something:")
#  rcv = port.read(10)
#  port.write("\r\nYou sent:" + repr(rcv))
