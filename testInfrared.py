import math
import time
import sys
import pygame
import smbus

bus = smbus.SMBus(1)     #There are two SMbus available on the R-Pi

pygame.init()

displayWidth = 190
displayHeight = 50
screen = pygame.display.set_mode((displayWidth,displayHeight))		# set display parameters of the window

# preset colours to use
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

font = pygame.font.SysFont('Avenir Next', 20)		# preset font to use

pygame.display.set_caption("Line Test")

def screen_display(irAngle, irRange):		
	screen.fill(black)		# set the screen background to black (should be anyway as default)
   
	screen.blit(font.render("IR Angle: ",True,white),(15,5))
	screen.blit(font.render(str(irAngle),True,white),(95,5))
	screen.blit(font.render("IR Range: ",True,white),(15,25))
	screen.blit(font.render(str(irRange),True,white),(95,25))

	pygame.display.update()		# update the display on each loop

def detect_close():
	for event in pygame.event.get():
		if event.type == pygame.QUIT:		# safe quit on closing the window
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:		# look for key presses
			if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:		# safe quit on "q" press or "ESC" press
				pygame.quit()
				sys.exit()

def read_IR_angle(address,angleControl,numBytes):
    rxBytes = bus.read_i2c_block_data(address, angleControl, numBytes)
    irAngle = rxBytes[0]*256 + rxBytes[1]
    irAngle = irAngle/11.32 -135
    
    return irAngle
    
def read_IR_range(address,rangeControl,numBytes):
    rxBytes = bus.read_i2c_block_data(address, rangeControl, numBytes) 
    irRange = rxBytes[2]*256 + rxBytes[3]

    return irRange

def main():
    address = 4
    rangeControl = 116
    angleControl = 116
    numBytes = 4
    
    while True:
		detect_close()
		
		irAngle = '{0:.2f}'.format(read_IR_angle(address,angleControl,numBytes))
		irRange = read_IR_range(address,rangeControl,numBytes)
		
		if irRange > 200:
			irRange = 200

		screen_display(irAngle, irRange)
		
main()
