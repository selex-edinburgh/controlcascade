# Traffic Lights

from Adafruit_MCP230xx import *
import time

mcp = Adafruit_MCP230XX(address = 0X20, num_gpios = 16)

mcp.config(0,mcp.OUTPUT) # red LED on pin 0 - set to output
mcp.config(3,mcp.OUTPUT) # yellow LED on pin 3 - set to output
mcp.config(7,mcp.OUTPUT) # green LED on pin 7 - set to output

while(True):
    mcp.output(0,1) # red on
    time.sleep(2) # wait 2 seconds
    mcp.output(3,1) # yellow on
    time.sleep(1) # wait 1 second
    mcp.output(0,0) # red off
    mcp.output(3,0) # yellow off
    mcp.output(7,1) # green on
    time.sleep (2) # wait two seconds
    mcp.output(7,0) # green off
    mcp.output(3,1) # yellow on
    time.sleep(1) # wait 1 second
    mcp.output(3,0) # yellow off
    
               
