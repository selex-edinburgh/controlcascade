#!/usr/bin/env python

#import libraries
import time
import sys
import pygame
import serial
import operator

try:
	import RPi.GPIO as GPIO
except RunTimeError as err:
	print err
	print "Error: Can't import RPi.GPIO"
	
pygame.init()

displayWidth = 190
displayHeight = 100
screen = pygame.display.set_mode((displayWidth,displayHeight))

pygame.display.set_caption("Line Test")

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

font = pygame.font.SysFont('Avenir Next', 20)

def read_raw(constants):
	# initialise local variables
    a = 0
    readbit = [0,0]
    packets = [0,0]
    
    GPIO.output(constants['CHIP_SELECT_PIN'],GPIO.HIGH)
    time.sleep(constants['TICK'])
    GPIO.output(constants['CLOCK_PIN'],GPIO.HIGH)
    time.sleep(constants['TICK'])
    GPIO.output(constants['CHIP_SELECT_PIN'],GPIO.LOW)
    time.sleep(constants['TICK'])
    
    while a < (constants['READING_BIT_LENGTH'] + constants['READING_LOW_0_BIT']):
        GPIO.output(constants['CLOCK_PIN'], GPIO.LOW)
        time.sleep(constants['TICK'])
        GPIO.output(constants['CLOCK_PIN'],GPIO.HIGH)
        time.sleep(constants['TICK'])
        
        readbit[0] = GPIO.input(constants['DATA_PIN_0'])
        readbit[1] = GPIO.input(constants['DATA_PIN_1'])
        
        packets[0] = ((packets[0] << 1) + readbit[0])
        packets[1] = ((packets[1] << 1) + readbit[1])
        
        a += 1
        
    return ((packets[1] << 16) | packets[0])

'''
	This function will take in a bit length and return a chunk of that
	number of a fixed length. This is called from the main().
'''
def bit_slicer(startBit, lowBit, count):
    sliceRange = 1 << count		
    mask = sliceRange - 1		
    return (startBit >> lowBit) & mask

'''
	This function will handle any rollovers that may occur during 
	runtime.
	It will detect if there is a jump in readings by > 512 and will 
	correct it.
	This is called from the main().
'''
def handle_rollovers(readings, constants):
	# initialise local variables
    prevReadings = [0,0]
    prevRollovers = [0,0]
    values = [0,0]
    
    rolloverRange = 1 << (constants['READING_BIT_LENGTH'] +1)
    big_jump = rolloverRange / 2
    for i in range(0,2):
        change = readings[i] - prevReadings[i]
        prevReadings[i] = readings[i]
        prevRollovers[i] += -1 if (change > big_jump) else (change < -big_jump)
        values[i] = readings[i] + (rolloverRange * prevRollovers[i])
    return values

'''
    This function will initialise the pins.
    It is passed in constants from the main() and uses them to set the pins
    to either input to output after initially clearing the pins to their
    default state.
'''
def init_pins(constants):
    
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setup(constants['DATA_PIN_0'], GPIO.IN)
    GPIO.setup(constants['DATA_PIN_1'], GPIO.IN)
    GPIO.setup(constants['CHIP_SELECT_PIN'], GPIO.OUT)
    GPIO.setup(constants['CLOCK_PIN'], GPIO.OUT)
    
'''
	This function will set up the serial interface. This setup uses a try
	and catch (except) that will catch any errors that may come up and 
	output a more verbose error to the user. During the setup it will 
	call the function versionCheck() to get the port value. This function 
	is called from main(). Line 115.
'''
def set_serial():
    try:
        ser= serial.Serial(                     #Set up Serial Interface
            port=version_check(),                #UART using Tx pin 8, Rx pin 10, Ground pin 6 
            baudrate=38400,                     #bits/sec
            bytesize=8, parity='N', stopbits=1, #8-N-1  protocal
            timeout=1                           #1 sec
        )
        return ser
    except Exception as err:
        print err
        print "Failed to setup serial"
        
'''
	Get the Revision Number of the Raspberry Pi. The Revision Number is 
	a unique number given to each Raspberry Pi model to distinguish each
	model. So all Raspberry Pi 2's will have the same Revision Number etc.
	This function will open up the cpuinfo file on the Raspberry Pi and
	look for the Revision Number. If found it will return it. This function
	is called from versionCheck(). Line 78.
'''
def get_revision():
	# initialise local variables
	cpuRevision = "0"
	
	try:		# try to open the file with the cpuinfo in it
		f = open('/proc/cpuinfo','r')
		for line in f:
			if line[0:8]=='Revision':		# if the characters from 0-8 == "Revision"
				cpuRevision = line[11:17]		# then set the cpu revision number to characters 11-17
		f.close()		# always close the file at the end
	
	except Exception as err:		# catch any exceptions that may occur when trying to open the file
                print err		# print the error that is caught and output the revision number as 0
                print "Failed to open file"
		cpuRevision = "0"
	
	return cpuRevision		# return the revision number to where the function was called from originally

'''
	This function will take the Revision Number it is passed when it calls
	the getRevision() function and will determine if it is either a 
	Raspberry Pi 2 or a Raspberry Pi 3. It will compare the value given
	with the two known Revision Numbers for either Pi. This will then
	determine the port value to return. This function is called from
	setSerial(). Line 30.
'''
def version_check():
	# initialise local variables
	port = "0"
	
	if get_revision() == 'a02082' or get_revision() == 'a22082':
		port = '/dev/ttyS0'
	elif get_revision() == 'a01041' or get_revision() == 'a21041':		
		port = '/dev/ttyAMA0'
	return port
	
'''
	This is a short function that is passed the serial interface so that
	it can simply read from the serial and output the results back to the
	call point. The ord function on the output changes ascii characters
	it receives from the read into the integer value of that character.
	This function is called from main(). Line 115.
'''
def get_telemetry(ser):
	try:
		telemetry = ser.read(4)
		return ord(telemetry[0]),ord(telemetry[1]) 	
	except Exception as err:
		print err
    
'''
This function will be the main function of the program. It creates a
Dictionary of constants that can be used in other functions.
The function will setup the GPIO pins and then run an infinite loop that
will read from the odometers, slice the reading into a readable chunk,
and then handle any rollovers that might occur before outputting the
result.
'''
def main():
	# initialise local variables
	crashed = False
	checkValue = [0,0]
	values = [0,0]
	fwd = 127
	turn = 127
	avgPos = 0
	readings = [0,0]
	differingValue = [0,0]
	
	# initialise the Dictionary
	constants = {
		'DATA_PIN_0' : 4,
		'DATA_PIN_1' : 18,
		'CHIP_SELECT_PIN' : 24,
		'CLOCK_PIN' : 23,
		'TICK' : 0.01,
		'READING_LOW_0_BIT' : 6,
		'READING_LOW_1_BIT' : 22,
		'READING_BIT_LENGTH' : 10,
		'ROLLOVER_RANGE' : 1023
	}

	init_pins(constants)		# initialise and setup the pins to use
	ser = set_serial()		# setup the serial

	while not crashed:		# infinite loop with a catch variable
		for event in pygame.event.get():
			if event.type == pygame.QUIT:		# safe quit on closing the window
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:		# look for key presses
				if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:		# safe quit on "q" press or "ESC" press
					pygame.quit()
					sys.exit()

		data = read_raw(constants)		# read from odometers

		readings[0] = bit_slicer(data,constants['READING_LOW_0_BIT'],constants['READING_BIT_LENGTH'])
		readings[1] = bit_slicer(data,constants['READING_LOW_1_BIT'],constants['READING_BIT_LENGTH'])

		values = handle_rollovers(readings,constants)		# handle rollovers
		
		leftReading = int(values[0])
		rightReading = int(constants['ROLLOVER_RANGE'] - values[1])
		
		avgPos = (leftReading + rightReading) / 2
		
		if fwd < 180:
			fwd = fwd + 1 
			
		ser.write(chr(fwd))
		
		screen.fill(black)		# set the screen background

		screen.blit(font.render("Odometers: (left, right)",True,white),(15,5))
		screen.blit(font.render(str((leftReading, rightReading)),True,white),(95,25))
		
		screen.blit(font.render("Telemetry: (forward, turn)",True,white),(15,45))
		screen.blit(font.render(str(get_telemetry(ser)),True,white),(110,65))
        
		pygame.display.update()        # update the display on each loop

main()		# start of the program
pygame.quit()
quit()
