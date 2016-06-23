#!/usr/bin/env python

# import libraries
import time
import sys
import serial
import pygame

pygame.init()		# initialise pygame

displayWidth = 190
displayHeight = 50
screen = pygame.display.set_mode((displayWidth,displayHeight))		# set display parameters of the window

pygame.display.set_caption("Motor Test")		# set title of the window

# preset colours to use
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

font = pygame.font.SysFont('Avenir Next', 20)		# preset font to use

'''
	This function will set up the serial interface. This setup uses a try
	and catch (except) that will catch any errors that may come up and 
	output a more verbose error to the user. During the setup it will 
	call the function versionCheck() to get the port value. This function 
	is called from main().
'''
def setSerial():
    try:
        ser= serial.Serial(                     #Set up Serial Interface
            port=versionCheck(),                #UART using Tx pin 8, Rx pin 10, Ground pin 6 
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
def getRevision():
	# initialise local variables
	cpurevision = "0"
	
	try:		# try to open the file with the cpuinfo in it
		f = open('/proc/cpuinfo','r')
		for line in f:
			if line[0:8]=='Revision':		# if the characters from 0-8 == "Revision"
				cpurevision = line[11:17]		# then set the cpu revision number to characters 11-17
		f.close()		# always close the file at the end
	
	except Exception as err:		# catch any exceptions that may occur when trying to open the file
                print err		# print the error that is caught and output the revision number as 0
                print "Failed to open file"
		cpurevision = "0"
	
	return cpurevision		# return the revision number to where the function was called from originally

'''
	This function will take the Revision Number it is passed when it calls
	the getRevision() function and will determine if it is either a 
	Raspberry Pi 2 or a Raspberry Pi 3. It will compare the value given
	with the two known Revision Numbers for either Pi. This will then
	determine the port value to return. This function is called from
	setSerial(). Line 30.
'''
def versionCheck():
	# initialise local variables
	port = "0"
	
	if getRevision() == 'a02082' or getRevision() == 'a22082':
		port = '/dev/ttyS0'
	elif getRevision() == 'a01041' or getRevision() == 'a21041':		
		port = '/dev/ttyAMA0'
	return port
	
'''
	This is a short function that is passed the serial interface so that
	it can simply read from the serial and output the results back to the
	call point. The ord function on the output changes ascii characters
	it receives from the read into the integer value of that character.
	This function is called from main().
'''
def getTelemetry(ser):
	try:
		telemetry = ser.read(4)
		return ord(telemetry[0]),ord(telemetry[1]) 	
	except Exception as err:
		print err

'''
	Here is where the first function call from when the program starts.
	The main will start off by initialising the two commands. Then it will
	set up the Serial Interface by calling setSerial. Finally a loop is 
	called that will listen and filter any keyboard events. 
	In this case it will listen for the key presses of: Q, ESC, Up, Down,
	Left and Right.
	Q and ESC will both safely kill the program. Up and Down will put the
	fwd up or down, and the Left and Right will change the turn by a positive
	or negative of 10 similar to fwd.
	These values are then written out to the Serial Interface and the 
	screen is then updated to show the results. 
'''
def main():
	# initialise local variables
    fwd = 127
    turn = 127
    crashed = False
    
    ser = setSerial()		# setup the serial

    # infinite loop / main loop / game loop
    while not crashed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:		# safe quit on closing the window
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:		# look for key presses
                if event.key == pygame.K_UP:
                    fwd += 10		# increase forward motion on arrow up
                elif event.key == pygame.K_DOWN:
                    fwd -= 10		# decrease forward motion on arrow down
                elif event.key == pygame.K_RIGHT:
                    turn += 10		# increase/decrease right/left turn on arrow key right
                elif event.key == pygame.K_LEFT:
                    turn -= 10		# increase/decrease left/right turn on arrow key left
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:		# safe quit on "q" press or "ESC" press
                    pygame.quit()
                    sys.exit()
        
        # write the resulting fwd and turn to the motors via serial
        ser.write(chr(fwd))
        ser.write(chr(turn))

        screen.fill(black)		# set the screen background to black (should be anyway as default)

        # display text to the screen, blit can also render images and draw on the screen
        screen.blit(font.render("Telemetry: (forward, turn)",True,white),(15,5))
        screen.blit(font.render(str(getTelemetry(ser)),True,white),(110,25))
        
        pygame.display.update()		# update the display on each loop

        time.sleep(0.016)		# sleep for 0.016 seconds

# program start
main()
pygame.quit()
quit()
