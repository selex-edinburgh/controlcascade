import smbus

### Used to communicate with the physical devices related to the components.
class i2c:

    def __init__(self, address):
        self.bus = smbus.SMBus() # Instance to allow library use
        self.address = address # the address of the slave device 

    ### Gets the version number of the Raspberry Pi board.
    ### This isn't wholly necessary and hopefully I haven't actually
    ### used it anywhere. 
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

    ### Reads the specified number of bytes from the i2c slave from 
    ### the specified register into a list. 
    def readList(self, reg, length):
        "Read a list of bytes from the I2C device"
        try:
            results = []
            results += self.bus.read_byte_data(self.address, reg)
            if length > 1: #If we are reading more than one byte
                for i in range (1, length):
                    # Add another result to the list
                    results += self.bus.read_byte_data(self.address + i, reg)
            return results
        except IOError, err:
          print "Error accessing 0x%02X: Check your I2C address" % self.address

    ### Writes a byte with the specified value to the slave on the
    ### specified register. 
    def write8(self, reg, value):
        "Writes an 8-bit value to the specified register"
        try:
          self.bus.write_byte_data(self.address, reg, value)
          print "I2C: Wrote 0x%02X to register 0x%02X" % (value, reg)
        except IOError, err:
          print "Error accessing 0x%02X: Check your I2C address" % self.address

