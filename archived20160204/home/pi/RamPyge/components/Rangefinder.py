
import smbus, sys, time
from i2c import i2c

### Class to encapsulate the idea and functions of a rangefinder sensor.

class Rangefinder:
    ### Constructor ( Rangefinder())
    def __init__(self, cfg):
        self.cfg = cfg
        self.connect = False
        if 'US_RANGER_ADDRESS' in self.cfg:
            self.connect = True
        else:
            print "WARNING: No rangefinder connected!"        #busnum = 1 if self.getPiRevision() > 1 else 0
        self.bus = i2c(self.cfg['US_RANGER_ADDRESS'])

    ### Returns the next availble readout in cm from the rangefinder.
    def read(self):
        self.bus.write8(self.cfg['US_REQUEST'], self.cfg['US_RANGE'])
        time.sleep(0.005)
        results = self.bus.readList(self.cfg['US_RANGE'],2) #Ranger output is composed of 2 bytes
        if results is not None:  
            result = (results[0] << 8) | results[1]
            return result/58 # Distance in mm
        else:
            return -1

## I2C TEST PROGRAM
if __name__ == '__main__':
    address = input("\nEnter address. ")
    cmd = input("\nEnter command register (or 0). ")
    reg = input("\nEnter register to read from. ")
    r = Rangefinder({'US_RANGER_ADDRESS':address, 'US_REQUEST':cmd, 'US_RANGE':reg})

    reading = r.read()
    print(reading) 
    time.sleep(0.2)
        
        
