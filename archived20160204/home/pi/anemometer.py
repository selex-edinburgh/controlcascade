from Adafruit_MCP230xx import *
import time
mcp = Adafruit_MCP230XX(address = 0X20, num_gpios = 16)
mcp.pullup(4, 1)
pulses = 0
start = time.time()
# run for ten seconds
while (time.time() < start + 10) :
    # wait for press or time up
    while (mcp.input(4) != 0 and time.time() < start + 10) :
        continue
    # count if press but not if we got here because time up
    if (mcp.input(4) == 0) :
        pulses = pulses + 1 # count the press
    # wait for release or time up
    while (mcp.input(4) == 0) :
            continue
print "number of pulses is %f" % pulses
