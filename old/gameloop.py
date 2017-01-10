'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import pygame
import os
import math
import runArcNodes

# it is better to have an extra variable, than an extremely long line.
#img_path = 'r2d2.png' #os.path.join('C:\Python27', 'player.png')
img_path = 'Tank.gif'

screenHeight = 720

screenWidth = 482

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  20, 150,   0)
RED =   (255,   0,   0)

class Robot(object):  # represents the Robot, not the game
    def __init__(self):
        """ The constructor of the class """
        self.image = pygame.image.load(img_path)
        # the Robot's position
        self.pos = (0,0)
        self.angle = 0
        self.targetPos = (0,0)
        self.scrBuff = None
        
        ##TEST
    def draw(self, surface):
        if self.scrBuff == None:
            self.scrBuff = surface.copy()
        surface.blit(self.scrBuff,(0,0))
        # blit yourself at your current position
        loc = self.image.get_rect().center
        rotImg = pygame.transform.rotate(self.image, 90.0 - self.angle)
        pygame.draw.line(self.scrBuff,BLACK,self.pos,self.pos, 4)
        rotImg.get_rect().center = loc
        surface.blit(rotImg, (self.pos[0] - rotImg.get_rect().width/2.0,
                              self.pos[1] - rotImg.get_rect().height/2.0))
        
        
    def handle_keys(self):
        """ Handles Keys """
        key = pygame.key.get_pressed()
        dist = 1 # distance moved in 1 frame, try changing it to  5
        if key[pygame.K_DOWN]: # down key
            self.pos[1] + dist # move down
        elif key[pygame.K_UP]: # up key
            self.pos[1] - dist # move up
        if key[pygame.K_RIGHT]: # right key
            self.pos[0] + dist # move right
        elif key[pygame.K_LEFT]: # left key
            self.pos[0] - dist # move left
        

    def updateRobot( obj, state ):
        robot.pos = (state.currentPos[0]/10.0, screenHeight -state.currentPos[1]/10.0)
        robot.angle = state.currentAngle #/ math.pi * 180.0
        robot.targetPos = (state.demandPos[0]/10.0, screenHeight - state.demandPos[1]/10.0) 
        robot.targetAngle =  state.demandAngle #/ math.pi * 180.0

class Course (object):
         
    def __init__(self):
        self.pole = (0,0)
        self.polePos = []
        self.newWaypoints = []
        
    
    def draw(self, surface):
    
        if robot.scrBuff == None:
            robot.scrBuff = surface.copy()
            
        pygame.draw.circle(robot.scrBuff,RED,(int(robot.targetPos[0]), int(robot.targetPos[1])), 4)
        
    def updateWaypoints(self):
        for w in self.newWaypoints:
            waypoint = (w[0], w[1])
            pygame.draw.circle(robot.scrBuff,WHITE,waypoint, 4,)
            pygame.draw.circle(robot.scrBuff,BLACK,waypoint, 4, 2)

            
    def updateObstacles(self,state):
  
        #background screen draw
        pygame.draw.polygon(robot.scrBuff, GREEN, [
            [120, 720],[120,480],
            [0,480],[0,0],
            [480,0],[480,480],
            [360,480],[360,720]])
        
        for w in state.wallList:
            self.wall = (w[0], screenHeight - w[1], w[2], screenHeight - w[3])
            pygame.draw.line(robot.scrBuff, BLACK, (self.wall[0], self.wall[1]), (self.wall[2], self.wall[3]), 4 )
            
        for p in state.poleList:
            self.pole = (p[0], screenHeight - p[1])
            pygame.draw.circle(robot.scrBuff,BLUE,self.pole, 10,)
            pygame.draw.circle(robot.scrBuff,BLACK,self.pole, 10, 2)
        
        pygame.display.update()
            
        
                        
    def addWaypoint(self, waypoint):
        self.newWaypoints.append(waypoint)

        
pygame.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))

robot = Robot() 
course = Course()
clock = pygame.time.Clock()

running = True
while running:
    # handle every event since the last frame.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() # quit the screen
            running = False
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            
            pos = (event.pos[0], screenHeight - event.pos[1])
           
            
            print "You pressed at locaton: ", pos
            course.addWaypoint(event.pos)
            course.updateWaypoints() #pass waypoint bac
    
    robot.handle_keys() # handle the keys

    screen.fill(WHITE) # fill the screen with white
    robot.draw(screen) # draw the Robot to the screen
    course.draw(screen) # draw the Course to the screen
    
    clock.tick(60)
    pygame.display.update() # update the screen
