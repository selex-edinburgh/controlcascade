import time, sys
import fcntl, os

def GeneratorFunction(max_val):
	with open("fifoY.tmp", 'r') as f:
		#fd = f.fileno()
		#flag = fcntl.fcntl(fd, fcntl.F_GETFL)
		#fcntl.fcntl(fd, fcntl.F_SETFL, flag) # | os.O_NONBLOCK)
		#flag = fcntl.fcntl(fd, fcntl.F_GETFL)
		#if flag:# & os.O_NONBLOCK:	
			while True:
				j = f.readline()
				yield "--> %s"%j

#def SmallGenerator():
#	for item in GeneratorFunction(10):
#		yield item
#
#for s in SmallGenerator():
#	print s

for s in GeneratorFunction(99999):
	print s
