import smbus, time

bus = smbus.SMBus(1)
addr = 0x04
reg = 0x00
byte1 = 41   # A
byte2 = 42   # B
byte3 = 43   # C
byte4 = 44   # D


# bus.write_byte_data(addr, reg, byte1)
# print "O.K. #2"

fourbytes = [byte1, byte2, byte3, byte4]
print fourbytes
bus.write_block_data(addr,reg, fourbytes)
vars = 2

bus.read_block_data(addr, vars)
print fourbytes


