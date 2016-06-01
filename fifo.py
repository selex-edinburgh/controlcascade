import time, datetime, sys
import fcntl, os

def GeneratorFunction():
	with open("fifo.tmp", 'r') as f:
			while True:
				j = f.readline()
				yield "%s"%j
f = open('out.txt', 'w')

for s in GeneratorFunction():
	now = datetime.datetime.now()
	someVariable = s
	someVariable = someVariable.strip().split(",")
	latency = float(now.microsecond) - float(someVariable[2])
	
	print 'Odometer1: {1} | Odometer2: {0} | Latency: {2:.0f}us | Difference 1/2: {3} {4}'.format(someVariable[0], someVariable[1], latency, someVariable[4], someVariable[3])
	bits = '{0:b}'.format(int(someVariable[5]))
	bits = bits.zfill(32)
	bitLength = len('{0}'.format(bits))
	
	print '32Bit: {0} | Bit Length: {1}'.format(bits, bitLength)
	slicedBits1 = '{0:b}'.format(int(someVariable[6]))
	slicedBits2 = '{0:b}'.format(int(someVariable[7]))
	print '10Bits: {0} {1}'.format(slicedBits2.zfill(10), slicedBits1.zfill(10))
	
	print >> f, '--------------------------------------------------'
	print >> f, 'Odometer 1:', someVariable[0], '|', '10 Bit:', slicedBits1.zfill(10), '|', 'Difference:', someVariable[3]
	print >> f, 'Odometer 2:', someVariable[1], '|', '10 Bit:', slicedBits2.zfill(10), '|', 'Difference:', someVariable[4]
	print >> f, '32 Bit Number:', bits
	print >> f, '--------------------------------------------------'
