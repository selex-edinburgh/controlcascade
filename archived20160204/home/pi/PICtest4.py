import smbus, time
bus = smbus.SMBus(1)

address = 4
control = 42    #READ 144=Odom, 84=Infa-Red current, 88=nearest during scan
               #WRITE 9-11=Scan, 7=Fixed Angle, 0=Redatum
numbytes = 4
Txbyte0 = -22
Txbyte1 = 22


## i2c sends bytes of 9 bits at 100K Baud
## bus WRITE sends Address with Write bit(0). control, Numbytes, Txbyte0, TxByte1
## bus READ sends  Address with Write bit(0), control, Restart,
##                 Address with Read bit(1), Rxbyte[0] to Rxbyte[3] 


Txbytes = [Txbyte0, Txbyte1 ]
bus.write_block_data(address, control, Txbytes)
print "Transmitted Bytes>", control, ", NoOfBytes,", Txbytes

#Rxbyte = bus.read_i2c_block_data(address, control, numbytes)
#print "Received Bytes>   ", Rxbyte[0], Rxbyte[1], Rxbyte[2], Rxbyte[3]


