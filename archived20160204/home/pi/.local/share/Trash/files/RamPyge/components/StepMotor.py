## Make sure the i2c port is enabled!

import smbus, sys, time

### StepMotor is a representation of the servo or stepper motor which the 
### distance ranging sensor is mounted on. Use a StepMotor object to control 
### the actions of the servo, and to read in its current bearing.
class StepMotor:

    ### Constructor ( StepMotor() )
    def __init__(self):
        #self.bus = smbus.SMBus(0)
        self.address = 0x00 # Change this to the address of the device
        self.MAX_ANGLE = 180
        self.MIN_ANGLE = 0

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
        pass

