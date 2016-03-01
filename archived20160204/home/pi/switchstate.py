# Example of testing switches

from Adafruit_MCP230xx import *
import time

mcp = Adafruit_MCP230XX(address = 0X20, num_gpios = 16)
mcp.pullup(4, 1)
mcp.config(0,mcp.OUTPUT)

while (True): #Run programme
    
    # wait for button press 
    while (mcp.input(4) != 0): #while switchstate is not zero
        continue # loop to while

    # button is pressed
    # delay 10ms to allow switch "bounce" to settle
    time.sleep(0.01)
    print "Switch pressed"

    

    


