from Adafruit_MCP230xx import *
import time
mcp = Adafruit_MCP230XX(address = 0X20, num_gpios = 16)
mcp.config(0,mcp.OUTPUT)
mcp.config(1,mcp.OUTPUT)
mcp.config(2,mcp.OUTPUT)
mcp.pullup(4, 1)

while(True) :  #Run programme

    mcp.output(0,1) #turn on pin 0 Red LED
    
    # wait for button press
    while (mcp.input(4) != 0): #input not zero 
        continue #loop to while
    
    # button is pressed  #input is zero
    mcp.output(0,1) #turn on pin 0 Red LED
    mcp.output(1,1) #turn on pin 1 LED Yellow
    time.sleep(3.0) # wait 3 seconds 
    mcp.output(0,0) #turn off pin 0 Red LED
    mcp.output(1,0) #turn off pin 1 LED Yellow
        
    mcp.output(2,1) #turn on pin 2 LED Green
    time.sleep(6.0) # wait 6 seconds
    mcp.output(2,0) #turn off pin 2 LED Green

    mcp.output(1,1) #turn on pin 1 LED Yellow
    time.sleep(3.0) # wait 3 seconds
    mcp.output(1,0) #turn off pin 1 LED Yellow
        
    mcp.output(0,1) #turn on pin 0 Red LED

