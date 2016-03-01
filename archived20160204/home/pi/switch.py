# Example of testing switches

from Adafruit_MCP230xx import *
import time

mcp = Adafruit_MCP230XX(address = 0X20, num_gpios = 16)

mcp.pullup(4, 1)

while (True):

    # wait for button press
    while (mcp.input(4) != 0):
        continue

    # delay 10ms to allow switch "bounce" to settle
    time.sleep(0.01)

    print "Switch pressed"

    # wait for button release
    while (mcp.input(4) == 0):
        continue
    
    # delay 10ms to allow switch "bounce" to settle
    time.sleep(0.01)

    print "Switch released"

    


