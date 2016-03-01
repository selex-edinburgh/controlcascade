import smbus, time
bus = smbus.SMBus(1)

address = 4
register = 0
numbytes = 4

Txbyte0 = 16
Txbyte1 = 17
Txbyte2 = 18
Txbyte3 = 19

## i2c sends bytes of 9 bits at 100K Baud
## bus WRITE sends
## bus READ sends Address with Write bit(0), Register, Restart,
##                Address with Read bit(1), Rxbyte[0] to Rxbyte[3] 


Txbytes = [Txbyte0, Txbyte1, Txbyte2, Txbyte3]
bus.write_block_data(address,register, Txbytes)
print "Transmitted Bytes>", Txbytes

#Rxbyte = bus.read_i2c_block_data(address, register, 4)
#print "Received Bytes>   ", Rxbyte[0], Rxbyte[1], Rxbyte[2], Rxbyte[3]


