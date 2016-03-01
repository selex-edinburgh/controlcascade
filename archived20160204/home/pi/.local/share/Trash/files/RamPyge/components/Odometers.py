import smbus, sys, time

### Represents the pair of odometers (for measuring chariot displacement from start position.) 
class Odometers:

    ### Constructor ( Odometers() )
    ### cg -> Global pulse to mm translation / correction- default 1.31 (float) 
    ### cl -> Translation/ correction offset for left wheel (float)
    ### cr -> Translation/ correction offset for right wheel (float)
    def __init__(self, cg, cl, cr):
        self.connect = False
        try:
            self.bus = smbus.SMBus(0)
            self.connect = True
        except:
            print "WARNING: No odometers connected!"
            
        self.address = 0x00 # Replace with device address
        self.corrGl = cg # Global correction
        self.corrL = cl # Left wheel correction offset
        self.corrR = cr # Right wheel correction offset

    ### Gets current odometer displacement readings.
    def read(self):
        if not self.connect:
            return [0, 0]
        #Read in 4 bytes:
        results = self.bus.read_i2c_block_data(self.address,0)
        try:
            #First 2 bytes = left count
            left = (results[0] << 8) | results[1]
            #Last 2 bytes = right count
            right = (results[2] << 8) | results[3]
        except:
            print "could not get odometer values"
            return -1

        #apply correction to counts - displacement = 1.31mm per count
            left *= (corrGl+corrL)
            right *= (corrGl+corrR)
        return [left, right]

    """
        ## Resets odometer distance.
        def reset(self):
            pass
    """

    ### Calculates the current bearing of the chariot through odometer readings.
    def getHeadingChange(self):
        left, right = self.read()
        change = right-left
        return change

    ### Calculates the displacement of the centre of the chariot from the starting position.
    def getDisplacement(self):
        left, right = self.read()
        disp = (left + right) / 2
        return disp

if __name__ == '__main__':
    #Display on screen
    o = Odometers(1.31, 0, 0) # Example with global correction only of 1.31
    print(o.read())
