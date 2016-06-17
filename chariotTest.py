import smbus
import serial
import time
import math
import sys
import subprocess as sub


def testOdometer(odoDriver,odoReadRate,odoPipename):
    cmd = ['sudo', 'chrt', '-f', '98',odoDriver,odoReadRate,odoPipename]
    try: 
        sub.Popen(cmd) #Run the C exe - Odometer Reader
    except Exception as err:
        print err

    self.generator = generatorFunction(odoPipename)
    
def GeneratorFunction():
	with open(odoPipename, 'r') as f:
			while True:
				j = f.readline()
				yield "%s"%j
                
def testSensorScanning():
    #Start I-R Scanning
    control = 42                            #Scan between two angles 
    Txbyte0 = 20                            #Left Scan Angle  -100 to +100 Degrees
    Txbyte1 = -20                           #Right Scan Angle -100 to +100 Degrees
    Txbyte0 = (Txbyte0 +135)*0.943 +0.5     #0.943 = Motor gearing of 11.32/12 to minimise PIC maths
    Txbyte1 = (Txbyte1 +135)*0.943 +0.5     #0.943 = Motor gearing of 11.32/12 to minimise PIC maths
    if Txbyte0 < 1: Txbyte0 =1              #Limit to Byte values
    if Txbyte0 > 254:  Txbyte0 =254         #Limit to Byte values
    if Txbyte1 < 1: Txbyte1 =1              #Limit to Byte values
    if Txbyte1 > 254: Txbyte1 =254          #Limit to Byte values
    Txbytes = [int(Txbyte0), int(Txbyte1) ]
    bus.write_block_data(address, control, Txbytes)   #Start I-R Scanning
    print "Infr-Red Ranger scanning between:",int(Txbyte0 /0.943-135),"and",int(Txbyte1 /0.943-135)

    time.sleep(0.5)
    
def testSensorReading():
    #Set Up I2C Serial Interface.
    bus = smbus.SMBus(1)     #There are two SMbus available on the R-Pi
    address = 4       	     #Seven bit Byte: as bit 8 is used for READ/WRITE designation.
    control = 33             #WRITE 42=Scan, 39=Fixed Angle, 33=Redatum stepper
                             #READ 144=Odom, 84=Infa-Red current, 88=nearest during scan
    numbytes = 4             #No of Bytes to be transmitted including control & numbytes
    Txbyte0 = 0              #Center
    Txbyte1 = 0              #Center
    Txbytes = [Txbyte0, Txbyte1 ]

    #Initialise Stepper Motor
    control = 33            #Initialise Stepper Motor at scan speed 1
    bus.write_block_data(address, control, Txbytes)     #I2C command: Redatum stepper motor
    #i2c sends bytes of 9 bits at 100K Baud
    #bus WRITE sends Address with Write bit(0). control, Numbytes, Txbyte0, TxByte1
    print "Stepper Motor Initialising"
    
    #Read Infra-Red Angle and Range
    IRangle = 5                                 #Initial number below 10 degrees
    while IRangle <10:                          #Wait until stepper angle increases to >10 deg
        control = 116                           #Send command to I-R Sensor for Angle and Range
        Rxbytes = bus.read_i2c_block_data(address, control, numbytes) #Send I-R Sensor Angle and Range
        #print "Received Bytes>   ", Rxbytes[0], Rxbytes[1], Rxbytes[2], Rxbytes[3]
        IRangle = Rxbytes[0]*256 + Rxbytes[1]   #Extract high and low bytes of I-R Angle deg
        IRangle = IRangle/11.32 -135   	    #Correct for steps to I-R Angle 		
        IRrange = Rxbytes[2]*256 + Rxbytes[3]   #Extract high and low bytes of I-R Angle deg	
#       IRrange = IRrange*ScaleIRrange          #Correct for range = 		
#        print "A   I-R Angle",int(IRangle),"degrees,   I-R Range",int(IRrange),"mm."
        time.sleep(0.5)                         #Test angle every half second
        
    while int(IRangle) > 0:                     #Wait until stepper angle reduces to <=0 deg
        control = 116                           #Send command to I-R Sensor for Angle and Range
        Rxbytes = bus.read_i2c_block_data(address, control, numbytes) #Send I-R Sensor Angle and Range
        #print "Received Bytes>   ", Rxbytes[0], Rxbytes[1], Rxbytes[2], Rxbytes[3]
        IRangle = Rxbytes[0]*256 + Rxbytes[1]   #Extract high and low bytes of I-R Angle deg
        IRangle = IRangle/11.32 -135   	        #Correct for steps to I-R Angle 		
        IRrange = Rxbytes[2]*256 + Rxbytes[3]   #Extract high and low bytes of I-R Angle deg	
#        IRrange = IRrange*ScaleIRrange         #Correct for range = 		
#        print "B   I-R Angle",int(IRangle),"degrees,   I-R Range",int(IRrange),"mm."
        time.sleep(0.5)                         #Test angle every half second

    print "Finished Stepper Motor Initialisation to Center"
    print "I-R Angle",int(IRangle),"degrees,   I-R Range",int(IRrange),"mm."
        
def testMotorOutput(serialDevice):
    try:
        #Set up Universal Asynchronous Receive-Transmit (UART) Serial Interface  ---------------------       
        ser= serial.Serial(                     #Set up Serial Interface				
            port=serialDevice,                  #UART using Tx pin 8, Rx pin 10, Gnd pin 6 		
            baudrate=38400,                     #bits/sec						
            bytesize=8, parity='N', stopbits=1, #8-N-1  protocol					
            timeout=1                           #1 sec							
        )
        fwd = input ("Input forward value (+/-80)? ")
        fwd = 127 - fwd

        turn = input ("Input turn value (+/-80? ")
        turn = 127 - turn

        while True:
            ser.write(chr(fwd))
            ser.write(chr(turn))
            #print (fwd, turn)                   #Remove to stop glitches
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        testMotorOutput(port)

def testStraightLine():
    pass
    
def main(argv):
    if (sys.argv[1] == "motorOutput"):
        if (sys.argv[2] == "pi2"):
            testMotorOutput("/dev/ttyAMA0")
        elif (sys.argv[2] == "pi3"):
            testMotorOutput("/dev/ttyS0")
    elif (sys.argv[1] == "straightLine"):
        testStraightLine()
    elif (sys.argv[1] == "odometer"):
        testOdometer(sys.argv[2],sys.argv[3],sys.argv[4])
        for s in GeneratorFunction():
            someVariable = s
            someVariable = someVariable.strip().split(",")
            print 'Odometer1: {0} | Odometer2: {1}'.format(someVariable[0], someVariable[1])
    elif (sys.argv[1] == "sensor"):
        testSensor()

if __name__ == "__main__":
    main(sys.argv[1:])