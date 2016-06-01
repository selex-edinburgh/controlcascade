import time, datetime, sys
import fcntl, os

def GeneratorFunction():
	#open the pipe for reading and yield from it
	with open("fifo.tmp", 'r') as f:
			while True:
				j = f.readline()
				yield "%s"%j
#open the file to write the outputs to later
f = open('out.txt', 'w')

for p in GeneratorFunction():
	#get the current time to compare later for latencies
	now = datetime.datetime.now()
	pipeMessage = p
	#splits the message into an array using CSV
	pipeMessage = pipeMessage.strip().split(",")
	odometer1 = pipeMessage[0]
	odometer2 = pipeMessage[1]
	#calculate latency by taking the time that's been passed through and taking the difference 
	latency = float(now.microsecond) - float(pipeMessage[2])
	odoDiff1 = pipeMessage[3]
	odoDiff2 = pipeMessage[4]
	#takes the bits from the message and will convert to raw bits
	#Full 32 raw bit data
	bits = '{0:b}'.format(int(pipeMessage[5]))
	#zfill will take a number and prefix it with 0's until it is the given size - here is 32
	bits = bits.zfill(32)
	#gets the length of the number - should be 32
	bitLength = len('{0}'.format(bits))
	#gets the 10 bit message fragments
	slicedBits1 = '{0:b}'.format(int(pipeMessage[6]))
	slicedBits2 = '{0:b}'.format(int(pipeMessage[7]))
	
	#Prints out to the screen
	print 'Odometer1: {1} | Odometer2: {0} | Latency: {2:.0f}us | Difference 1/2: {3} {4}'.format(odometer1, odometer2, latency, odoDiff2, odoDiff1)
	
	print '32Bit: {0} | Bit Length: {1}'.format(bits, bitLength)
	print '10Bits: {0} {1}'.format(slicedBits2.zfill(10), slicedBits1.zfill(10))
	
	#Prints out to the file out.txt
	print >> f, '--------------------------------------------------'
	print >> f, 'Odometer 1:', odometer1, '|', '10 Bit:', slicedBits1.zfill(10), '|', 'Difference:', odoDiff1
	print >> f, 'Odometer 2:', odometer2, '|', '10 Bit:', slicedBits2.zfill(10), '|', 'Difference:', odoDiff2
	print >> f, '32 Bit Number:', bits
	print >> f, '--------------------------------------------------'
