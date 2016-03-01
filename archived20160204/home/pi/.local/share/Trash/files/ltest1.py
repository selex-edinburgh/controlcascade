import serial
import time

port = serial.Serial("/dev/ttyAMA0", 9600, )

while True:
  port.write("\r\nSay something:")
  rcv = port.read(10)
  port.write("\r\nYou sent:" + repr(rcv))
