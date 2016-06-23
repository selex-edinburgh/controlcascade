#!/usr/bin/env python

# import libraries
import time
import sys
import pygame
import operator

try:		# try and import the GPIO library and catch a RunTimeError on fail
    import RPi.GPIO as GPIO
except RunTimeError as err:		# catch the RunTimeError and output a substitute response
    print err
    print ("Error: Can't import RPi.GPIO")
   
pygame.init()		# initialise pygame

displayWidth = 190
displayHeight = 50
screen = pygame.display.set_mode((displayWidth,displayHeight))		# set display parameters of the window

pygame.display.set_caption("Odo Test")		# set title of the window

# preset colours to use
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

font = pygame.font.SysFont('Avenir Next', 20)		# preset font to use

'''    
   This function will read from the odometers directly and pass the
   result back to the main(). It uses the GPIO libraries to clock the 
   pins high and low to tell the odometers when to start outputting data.
    
'''
def read_raw(constants):
	# initialise local variables
    a = 0
    dataPin0 = 0
    dataPin1 = 0
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
	readings = [0,0]
	differingValue = [0,0]
	init_reading_0 = [0,0]
	
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
		
		screen.fill(black)		# set the screen background

		screen.blit(font.render("Odometers: (left, right)",True,white),(15,5))
		screen.blit(font.render(str((int(values[0]), int(constants['ROLLOVER_RANGE']-values[1]))),True,white),(95,25))

		pygame.display.update()        # update the display on each loop

main()		# start of the program
pygame.quit()
quit()
