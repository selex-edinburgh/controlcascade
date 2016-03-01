
import smbus, sys, time

### Class to encapsulate the idea and functions of a rangefinder sensor.
class Rangefinder:
    ### Constructor ( Rangefinder() )
    def __init__(self):
        #self.bus = smbus.SMBus(0)
        self.address = 0x00 #replace with device address

    def __init__(self, address):
        self.address = address
        #busnum = 1 if self.getPiRevision() > 1 else 0
        self.bus = smbus.SMBus()

    ### Returns the next availble readout in cm from the rangefinder.
    def read(self):
        #return ord(self.bus.read_byte(address))/58
        return 0

    def read(self, register):
        pass

    

    @staticmethod
    def getPiRevision():
        "Gets the version number of the Raspberry Pi board"
        # Courtesy quick2wire-python-api
        # https://github.com/quick2wire/quick2wire-python-api
        try:
          with open('/proc/cpuinfo','r') as f:
            for line in f:
              if line.startswith('Revision'):
                return 1 if line.rstrip()[-1] in ['1','2'] else 2
        except:
          return 0

    def readList(self, reg, length):
        "Read a list of bytes from the I2C device"
        try:
            results = []
            results += self.bus.read_byte_data(self.address, reg)
            if length > 1:
                for i in range (1, length):
                    results += self.bus.read_byte_data(self.address + i, reg)
            print results
        except IOError, err:
          print "Error accessing 0x%02X: Check your I2C address" % self.address

    def write8(self, reg, value):
        "Writes an 8-bit value to the specified register"
        try:
          self.bus.write_byte_data(self.address, reg, value)
          print "I2C: Wrote 0x%02X to register 0x%02X" % (value, reg)
        except IOError, err:
          print "Error accessing 0x%02X: Check your I2C address" % self.address

## I2C TEST PROGRAM
if __name__ == '__main__':
    address = input("\nEnter address. ")
    cmd = input("\nEnter command register (or 0). ")
    cmdv = input("\nEnter command value (or 0). ")
    reg = input("\nEnter register to read from. ")
    ln = input("\nEnter expected number of bytes ")
    r = Rangefinder(address)

    while True:
        if cmd != 0:
            r.write8(cmd, cmdv)
            time.sleep(0.005)
        
        r.readList(reg, ln)
        time.sleep(1)
