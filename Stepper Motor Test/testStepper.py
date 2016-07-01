#!/usr/bin/env python

# import libraries
import smbus
import time
import serial

bus = smbus.SMBus(1)        # set up the smbus interface

def init_stepper(busData, controlCodes):
	print "Initialising Stepper"
	try:
		bus.write_block_data(busData['address'],controlCodes['initMotor'],busData['txBytes'])
	except Exception as err:
		print err
		print "Failed to write to the bus"
	
def rotate_stepper(busData, controlCodes):
	print "Attempting rotation"
	try:
		bus.write_block_data(busData['address'],controlCodes['betweenAngles'],[20,-20])
	except Exception as err:
		print err
	
def read_angle(busData, controlCodes):
	rxBytes = bus.read_i2c_block_data(busData['address'], controlCodes['readAngle'],0)
	return rxBytes
	
def main():
	busData = {
	'address' : 4,
	'txBytes' : [0,0],
	'rxBytes' : 0, 
	'numBytes': 4
	}
	
	controlCodes = {
	'stop' : 32,
	'initMotor' : 33,
	'fixedAngle' : 39,
	'betweenAngles' : 42,
	'readAngle' : 116
	}
	
	init_stepper(busData,controlCodes)
	time.sleep(5)
	rotate_stepper(busData,controlCodes)
	
main()
