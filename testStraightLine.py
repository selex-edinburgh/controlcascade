#!/usr/bin/env python

#import libraries
import testMotor as motor
import testOdometer as odo
import pygame
import time
import sys

pygame.init()

displayWidth = 190
displayHeight = 100
screen = pygame.display.set_mode((displayWidth,displayHeight))		# set display parameters of the window

# preset colours to use
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

font = pygame.font.SysFont('Avenir Next', 20)		# preset font to use

pygame.display.set_caption("Line Test")

def screen_display():
	# display text to the screen, blit can also render images and draw on the screen
	screen.blit(font.render("Telemetry: (forward, turn)",True,white),(15,5))
	screen.blit(font.render(str(motor.get_telemetry(ser)),True,white),(110,25))
	screen.blit(font.render("Odometers: (left, right)",True,white),(15,45))
	screen.blit(font.render(str((int(values[0]), int(constants['ROLLOVER_RANGE']-values[1]))),True,white),(95,65))

def main():
	# initialise local variables
	crashed = False
	fwd = 127
	turn = 127
	readings = [0,0]
	init_readings = [0,0]
	is_first = 0
	
	ser = motor.set_serial()
	
	while not crashed:
		odo.detect_close()		# detect for quit, Q, or ESC to exit program
		constants = odo.init_pins()		# initialise the pins and create the constants dictionary
		ser.write(chr(fwd))
		ser.write(chr(turn))
		
		data = odo.read_raw(constants)		# read from odometers
		
		if is_first != 0:
			readings[0] = odo.bit_slicer(data,constants['READING_LOW_0_BIT'],constants['READING_BIT_LENGTH'])
			readings[1] = odo.bit_slicer(data,constants['READING_LOW_1_BIT'],constants['READING_BIT_LENGTH'])
		else:
			is_first = -1
			init_readings[0] = odo.bit_slicer(data,constants['READING_LOW_0_BIT'],constants['READING_BIT_LENGTH'])
			init_readings[1] = odo.bit_slicer(data,constants['READING_LOW_1_BIT'],constants['READING_BIT_LENGTH'])
			
		
		
		values = odo.handle_rollovers(readings,constants)		# handle rollovers
		
		screen.fill(black)		# set the screen background to black (should be anyway as default)
        
		pygame.display.update()		# update the display on each loop

		time.sleep(0.016)		# sleep for 0.016 seconds
		
if __name__ == "__main__":
	main()
	pygame.quit()
	quit()
