import time, datetime, sys
import fcntl, os

def GeneratorFunction():
	with open("fifo.tmp", 'r') as f:
			while True:
				j = f.readline()
				yield "%s"%j

for s in GeneratorFunction():
	now = datetime.datetime.now()
	someVariable = s
	someVariable = someVariable.strip().split(",")
	latency = float(now.microsecond) - float(someVariable[2])	
	print 'Odometer1: {0} | Odometer2: {1} | Latency: {2:.0f}us'.format(someVariable[0], someVariable[1], latency)
