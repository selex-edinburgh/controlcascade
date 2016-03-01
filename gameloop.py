import pygame
import os
import math
import runControlLoops

# it is better to have an extra variable, than an extremely long line.
#img_path = 'r2d2.png' #os.path.join('C:\Python27', 'player.png')
img_path = 'Tank.gif'

screenHeight = 600
screenWidth = 800

class Board(object):  # represents the Board, not the game
    def __init__(self):
        """ The constructor of the class """
        self.image = pygame.image.load(img_path)
        # the Robot's position
        self.robotPos = (0,0)
        self.robotAngle = 0
        self.robotTargetPos = (0,0)
        self.scrBuff = None
        
    """def handle_keys(self):
        "" Handles Keys ""
        key = pygame.key.get_pressed()
        dist = 1 # distance moved in 1 frame, try changing it to 5
        if key[pygame.K_DOWN]: # down key
            self.pos[1] += dist # move down
        elif key[pygame.K_UP]: # up key
            self.pos[1] -= dist # move up
        if key[pygame.K_RIGHT]: # right key
            self.pos[0] += dist # move right
        elif key[pygame.K_LEFT]: # left key
            self.pos[0] -= dist # move left"""
        
    def draw(self, surface):
        if self.scrBuff == None:
            self.scrBuff = surface.copy()
        """ Draw on surface """
        pygame.draw.line(self.scrBuff,0,self.robotPos,self.robotTargetPos)
        surface.blit(self.scrBuff,(0,0))
        # blit yourself at your current position
        loc = self.image.get_rect().center
        rotImg = pygame.transform.rotate(self.image, 90.0 - self.robotAngle)
        rotImg.get_rect().center = loc
        surface.blit(rotImg, (self.robotPos[0] - rotImg.get_rect().width/2.0,
                              self.robotPos[1] - rotImg.get_rect().height/2.0))
        
pygame.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))

board = Board() # create an instance
clock = pygame.time.Clock()

    
def boardUpdate( obj, state ):
    board.robotPos = (state.currentPos[0]/10.0, screenHeight -state.currentPos[1]/10.0)
    board.robotAngle = state.currentAngle 
    board.robotTargetPos = (state.demandPos[0]/10.0, screenHeight - state.demandPos[1]/10.0) 
    board.robotTargetAngle =  state.demandAngle 
    
runControlLoops.runControlLoops(
     type('testclass', (object,), 
                                 {'update':boardUpdate})()
                            )


running = True
while running:
    # handle every event since the last frame.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() # quit the screen
            running = False

    #board.handle_keys() # handle the keys

    screen.fill((255,255,255)) # fill the screen with white
    board.draw(screen) # draw the Robot to the screen
    
    clock.tick(60)
    pygame.display.update() # update the screen
