import serial, sys, time, smbus
from i2c import i2c

### Represents the pair of odometers (for measuring chariot displacement from start position.) 
class Odometers:

    ### Constructor ( Odometers() )
    ### cg -> Global pulse to mm translation / correction- default 1.31 (float) 
    ### cl -> Translation/ correction offset for left wheel (float)
    ### cr -> Translation/ correction offset for right wheel (float)
    def __init__(self, cfg, cg, cl, cr):
        self.cfg = cfg
        self.usingSerial = False
        self.connected = False
        try:
            self.port = serial.Serial("/dev/ttyANA1",baudrate=57600,timeout=1)
            self.usingSerial = True
            self.connected = True
        except:
            if not self.connected:
                print "WARNING: No odometers connected!"
            
        self.address = 0x00 # Replace with device address
        self.corrGl = cg # Global correction
        self.corrL = cl # Left wheel correction offset
        self.corrR = cr # Right wheel correction offset

        self.runningDisplacement = 0

        self.bus = i2c(cfg['ODOM_ADDRESS'])


    ### Gets current odometer displacement readings.
    def read(self):
        if not self.usingSerial:
            try:
                i2c.write(cfg['OD_REQUEST'], '0')
                results = i2c.readList(cfg['OD_DISPS'],4)
            except:
                return [0,0]
        else:
            try:
                results = self.port.read(4)
            except:
                return [0, 0]
        try:
            #First 2 bytes = left count
            left = (results[0] << 8) | results[1]
            #Last 2 bytes = right count
            right = (results[2] << 8) | results[3]
        except:
            print "could not get odometer values"
            self.connected = False
            return -1

        #apply correction to counts - displacement = 1.31mm per count
            left *= (corrGl+corrL)
            right *= (corrGl+corrR)
            self.connected = True
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

    ### Calculates by how much the displacement of the chariot has changed since the
    ### last time that this function was called
    def getDisplacementChange(self):
        result = self.getDisplacement() - self.runningDisplacement
        self.runningDisplacement = self.getDisplacement()
        return result

    ### Calculates the displacement of the centre of the chariot from the starting position.
    def getDisplacement(self):
        left, right = self.read()
        disp = (left + right) / 2
        return disp

if __name__ == '__main__':
    #Display on screen
    o = Odometers(1.31, 0, 0) # Example with global correction only of 1.31
    print(o.read())
