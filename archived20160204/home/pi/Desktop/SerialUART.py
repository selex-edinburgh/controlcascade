#serial_write.py
#!/usr/bin/env python

import time
import serial, sys

def main():
    try:
        ser= serial.Serial(                     #Set up Serial Interface
            port="/dev/ttyAMA0",                #UART using Tx pin 8, Rx pin 10, Ground pin 6 
            baudrate=9600,                      #bits/sec
            bytesize=8, parity='N', stopbits=1, #8-N-1  protocal
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
        main()
main()





















        #counter=0               
        #while 1:
        #    ser.write('Write counter: %d \n'%(counter))
        #    time.sleep(1)
        #    counter += 1

        #while True:
        #    ser.write('Write counter: %d \n'%(counter))   #OK, %d = placeholder for 
        #    print counter             # OK
        #    print "%d" % (counter)    # OK
        #    print "%d" \n" % (counter) # ? 
        #    time.sleep(1)
        #    counter=counter+1
            
        #serial_read.py
        #!/usr/bin/env python
                        
        #import time
        #import serial
                  
        #ser = serial.Serial(           
        #    port='/dev/ttyUSB0',
        #    baudrate = 9600,
        #    parity=serial.PARITY_NONE,
        #    stopbits=serial.STOPBITS_ONE,
        #    bytesize=serial.EIGHTBITS,
        #    timeout=1
        #)
        #counter=0
        #           
        #while 1:
         #   x=ser.readline()
          #  print x

          
#    except KeyboardInterrupt:
#        main()
#main()       
