## Make sure the i2c port is enabled!

import smbus, sys, time
from i2c import i2c

### StepMotor is a representation of the servo or stepper motor which the 
### distance ranging sensor is mounted on. Use a StepMotor object to control 
### the actions of the servo, and to read in its current bearing.
class StepMotor:

    ### Constructor ( StepMotor() )
    def __init__(self, cfg):
        self.cfg = cfg
        self.MAX_ANGLE = 180
        self.MIN_ANGLE = 0
        self.i2c = i2c(self.cfg['STEPM_ADDRESS'])

        if 'STEPM_ADDRESS' in self.cfg:
            self.connect = True
        else:
            self.connect = False
            print "WARNING: No stepmotor connected!"

    ### Sends a signal indicating to move in the default range of motion.    
    def scan(self):
        transmit('s')

    ### Sends a signal indicating to use a restricted range of motion.
    def restrict(self, min, max):
        transmit('r')
        transmit(min)
        transmit(max)

    ### Send a signal to change speed with appropriate values.
    ### ss -> the new step size in whole degrees (int)
    ### delay -> the new delay between steps (int)
    def setSpeed(self, ss,delay):
        transmit('v')
        transmit(ss)
        transmit(delay)

    ### Sends a signal telling the servo to change direction.
    def reverse(self):
        transmit('i')

    ### Sends a signal telling the servo to stop moving.
    def stop(self):
        transmit('0')

    ### Sends a signal telling the servo to move to and stay at a position.
    ### pos -> the bearing in whole degrees to move to (int)
    def move(self, pos):
        transmit('R')
        transmit(chr(pos))

    ### Writes the appropriate command byte over the i2c bus.
    def transmit(self, data):
        #self.bus.write_byte(self.address,data)
        pass

    ### Reads in the current servo position.
    def read(self):
        """
        self.bus.write8(self.cfg['US_REQUEST'], self.cfg['US_RANGE'])
        time.sleep(0.005)
        results = self.bus.readList(self.cfg['US_RANGE'],2) #Ranger output is composed of 2 bytes
        if results is not None:  
            result = (results[0] << 8) | results[1]
            return result/58 # Distance in mm
        else:
            return -1"""
        pass


## TEST SCRIPT
if __name__ == '__main__':
    address = input("\nEnter address. ")
    cmd = input("\nEnter command register (or 0). ")
    reg = input("\nEnter register to read from. ")
    s = StepMotor(address)

