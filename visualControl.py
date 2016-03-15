import pygame
import math
import sys
import os
from gamelib import *
from  pygame import gfxdraw
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator
from pygame.locals import *


progname = sys.argv[0]      # lib import for right-click menu
progdir = os.path.dirname(progname)
sys.path.append(os.path.join(progdir,'gamelib'))
from popup_menu import NonBlockingPopupMenu

BLACK = (  0,   0,   0)     # global constants
WHITE = (255, 255, 255) 
BLUE =  (  147,   179, 208)
LIGHT_BLUE = (120,135,171)
GREEN = (  34, 102,   102)
RED =   (192,   57,   43)
GREY = (52,73,94)
TRAIL_GREY = (44,62,80)
MARGIN = 200

pygame.init()

menu_data = (
    'Main',
    'Add Waypoint',
    'Remove Last Waypoint',
    'Pause Loops',
    'Resume Loops',
    (
        'Things',
        'Item 0',
        'Item 1',
        'Item 2',
        (
            'More Things',
            'Item 0',
            'Item 1',
        ),
    ),
    'Remove Pole',
    'Quit',
)

class VisualState(ObservableState):
    def __init__(self):
        super(VisualState,self).__init__()
        
        self.screenWidth = 682      # set screen height and width
        self.screenHeight = 720
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))       
        pygame.display.set_caption('\t \t \tVisualiser')       # screen caption        
        self.font = pygame.font.SysFont('Avenir Next', 16)        # different fonts used in the program
        self.fontTitle = pygame.font.SysFont('Avenir Next',22)                 
        self.image = pygame.image.load('images/robot.png')       # robot image
        self.imageCompass = pygame.image.load('images/compass.png')
        self.imageCompass.convert()
        self.wallList = []      # enviromentals
        self.poleList = []
        self.goalList = []
        self.barrelList = []
        self.barrierList= []
        self.ballList = []
        self.poleRecList = []       # used for collision detection
        self.waypoint = (0,0)       # list of waypoints       
        self.robotPos = (0,0)       # current position of robot
        self.robotAngle = 0     # current angle of robot
        self.targetPos = (0,0)      # next waypoint      
        self.prevWaypoint = (0,0)       # previous waypoints   
        self.waypointList = []
        self.scrBuff = None        
        self.scanCone = ((0,0),(0,0),(0.0))     # scan used for collison range
        self.isCollision = False    # bool to check if pole in collision range  
        self.nearWaypoint = False     # bool to check if near waypoint      
        self.removeLastWP = False       # remove last waypoint if true
        self.rcFwd = 0      #information panel data for motors
        self.rcTurn = 0        
        self.leftReading = 0        #information panel data for odometers
        self.rightReading = 0     
        self.maxLatency = 0       #information panel data for control loops
        self.minLatency = 0
        self.averageLatency = 0
        self.lengthOfBatch = 0
        self.varianceOfLatency = 0
        
        self.realMode = False
  
        self.pauseLoops = False
        self.menu = NonBlockingPopupMenu(menu_data)      # define right-click menu
        
    def drawRobot(self, surface):
        if self.scrBuff == None:
                self.scrBuff = surface.copy()
        surface.blit(self.scrBuff,(0,0))
        loc = self.image.get_rect().center
        rotImg = pygame.transform.rotate(self.image, 90.0 - self.robotAngle)
        rotImg.get_rect().center = loc
        
        surface.blit(rotImg, ((self.robotPos[0] ) - rotImg.get_rect().width/2.0,
                              self.robotPos[1] - rotImg.get_rect().height/2.0))
        
        if self.isCollision == False: 
            pygame.draw.lines(surface, BLACK, True, ((self.scanCone[0]), self.scanCone[1], self.scanCone[2]), 2)
        else:
            pygame.draw.lines(surface, RED, True, ((self.scanCone[0]), self.scanCone[1], self.scanCone[2]), 2)

    def drawPath(self,surface):
           
        pygame.draw.circle(surface,BLACK,(int(self.targetPos[0] ), int(self.targetPos[1])), 4)                # draw the red dot on the current waypoint and previously met ones
        pygame.draw.line(surface,TRAIL_GREY, self.robotPos,self.robotPos, 4)      


    def drawWaypoints(self, surface):
        for w in self.waypointList:
            pygame.draw.circle(surface,WHITE,(int(w[0] /10), int(self.screenHeight - w[1] /10)), 4,)
            pygame.draw.circle(surface,BLACK,(int(w[0] /10), int(self.screenHeight - w[1] /10)),4,2)
    def checkForCollision(self):
        self.poleRecList = []
        for p in self.poleList:
            poleRec = pygame.Rect(p[0] - 10, (self.screenHeight - p[1] ) - 10 , 20,20)
            self.poleRecList.append(poleRec)

        chariotRec = pygame.Rect((self.robotPos[0] - 5, (self.screenHeight - self.robotPos[1])+ 5), (65,65)) 

        for r in self.poleRecList:
            if chariotRec.colliderect(r):
                pass

    def drawObstacles(self,surface):
        for wall in self.wallList:      # draw the walls on the screen
            self.wall = (wall[0], self.screenHeight - wall[1],  wall[2], self.screenHeight - wall[3])
            pygame.draw.line(surface, BLACK, (self.wall[0], self.wall[1]), (self.wall[2], self.wall[3]), 4 )
            
        for pole in self.poleList:      # draw poles on the screen
            self.pole = ( pole[0], self.screenHeight - pole[1])
            pygame.draw.circle(surface,BLUE,self.pole, 10,)
            pygame.draw.circle(surface,BLACK,self.pole, 10, 2)
            
        for goal in self.goalList:
            self.goal = (goal[0], self.screenHeight - goal[1], goal[2], self.screenHeight - goal[3])
            pygame.draw.line(surface,BLACK,(self.goal[0],self.goal[1]),(self.goal[2],self.goal[3]), 4)
        
        for barrier in self.barrierList:
            self.barrier = (barrier[0], self.screenHeight - barrier[1], barrier[2], self.screenHeight - barrier[3])
            pygame.draw.line(surface,BLACK,(self.barrier[0],self.barrier[1]),(self.barrier[2], self.barrier[3]), 3)
        for ball in self.ballList:
            self.ball = (ball[0], self.screenHeight - ball[1])
            pygame.draw.circle(surface,WHITE,self.ball, 7)
        
        pygame.draw.line(surface,WHITE, (5, 500), (5, self.screenHeight -5), 2)      # draw y axis
        surface.blit(self.font.render(("North"), True, WHITE), (10,500))
        surface.blit(self.fontTitle.render(("Y"), True, WHITE), (10,600))
        
        pygame.draw.line(surface,WHITE, (5, self.screenHeight - 5 ), (100, self.screenHeight- 5), 2)      # draw x axis
        surface.blit(self.font.render(("East"), True, WHITE), (80,(self.screenHeight - 22))) 
        surface.blit(self.fontTitle.render(("X"), True, WHITE), (50,(self.screenHeight - 22))) 
        
        origin = pygame.Rect(-5,self.screenHeight - 25, 40,40)
        pygame.draw.arc(surface, WHITE, origin, 0,2.2, 4)
        
        
    def drawInfoPanel(self,surface):
 
        surface.blit(self.fontTitle.render(("Robot Position"), True, WHITE), (505,(self.screenHeight -710)))     # robotPos information panel
        surface.blit(self.font.render(("X,Y (mm):  ({0},{1})".format(int(self.robotPos[0]), self.screenHeight - int(self.robotPos[1]))), True, WHITE), (505,self.screenHeight - 675))
        surface.blit(self.font.render(("Heading:   {0}".format(int(self.robotAngle))), True, WHITE), (505,self.screenHeight -655))  
            
        surface.blit(self.fontTitle.render(("Route"), True, WHITE), (505,(self.screenHeight -600)))     # latency information panel
        surface.blit(self.font.render(("Current Waypoint:  ({0},{1})".format(int(self.targetPos[0]), self.screenHeight - int(self.targetPos[1]))), True, WHITE), (505,self.screenHeight -565))
        surface.blit(self.font.render(("No. Of Waypoints:  {0}".format(len(self.waypointList) -1)), True, WHITE), (505,self.screenHeight -545))
        surface.blit(self.font.render(("Near Target:            %s" % (self.nearWaypoint)), True, WHITE), (505,self.screenHeight -525))
        
        surface.blit(self.fontTitle.render(("Sensor"), True, WHITE), (505,(self.screenHeight -475)))     # collision information panel
        surface.blit(self.font.render(("Obstacle in Range: %s" % (self.isCollision)), True, WHITE), (505,(self.screenHeight -440)))
       # surface.blit(self.imageCompass,( 470, self.screenHeight - 240 ))
        if self.realMode:
            surface.blit(self.font.render(("Non-Simulated mode"), True, WHITE),(565,(self.screenHeight - 20)))
        else:
            surface.blit(self.font.render(("Simulated mode"), True, WHITE),(555,(self.screenHeight - 20)))
        
        pos = pygame.mouse.get_pos()
        pos = (pos[0], self.screenHeight - pos[1] )
        surface.blit(self.font.render(("Cursor pos:  {0}".format(pos)),True, WHITE), (555, self.screenHeight - 40))
        if self.pauseLoops:
            surface.blit(self.font.render(("Paused..."), True, WHITE), (555, self.screenHeight - 60))
        """
        REDUNDENT FOR NOW
        surface.blit(self.fontTitle.render(("Motor Data"), True, BLACK), (505,(self.screenHeight -305)))     # latency information panel
        surface.blit(self.font.render(("Turn Command: %s" % int((self.rcTurn))), True, BLACK), (505,(self.screenHeight -250)))
        surface.blit(self.font.render(("Fwd Command: %s" % int((self.rcFwd))), True, BLACK), (505,(self.screenHeight -270)))
        
        surface.blit(self.fontTitle.render(("Odometer Data"), True, BLACK), (505,(self.screenHeight -190)))     # latency information panel
        surface.blit(self.font.render(("Left Reading: %s" % int((self.leftReading))), True, BLACK), (505,(self.screenHeight -155)))
        surface.blit(self.font.render(("Right Reading: %s" % int((self.rightReading))), True, BLACK), (505,(self.screenHeight -135)))   # update the screen
        
        surface.blit(self.font.render(("Max (s):        {0:.3f}".format(self.maxLatency)), True, BLACK), (505,self.screenHeight -520))
        surface.blit(self.font.render(("Min (s):         {0:.3f}".format(self.minLatency)), True, BLACK), (505,self.screenHeight -500))
        surface.blit(self.font.render(("Average (s):  {0:.3f}".format(self.averageLatency)), True, BLACK), (505,self.screenHeight -480))
        surface.blit(self.font.render(("Msg Length:  {0}".format(self.lengthOfBatch)), True, BLACK), (505,self.screenHeight -460))
        surface.blit(self.font.render(("Variance:       {0:.3f}".format(self.varianceOfLatency)), True, BLACK), (505,self.screenHeight -440))
        """
def handle_menu(e, state):
    print 'Menu event: %s.%d: %s' % (e.name,e.item_id,e.text)
    
    if e.name is None:
        print 'Hide menu'
        state.menu.hide()
    elif e.name == 'Main':
        print e.originalEvent.pos
        if e.text == 'Quit':
            pygame.quit()  
        if e.text == 'Pause Loops':
            state.pauseLoops = True
        if e.text == 'Resume Loops':
            state.pauseLoops = False
        if e.text == 'Remove Last Waypoint':
            state.removeLastWP = True
            
        if e.text == 'Remove Pole':
            pressPosition = (e.originalEvent.pos[0], e.originalEvent.pos[1])
            print pressPosition
            for index, r in enumerate(state.poleRecList, start = 0):
                if r.collidepoint(pressPosition):
                    state.poleList.pop(index)
                    state.poleRecList.pop(index)
    elif e.name == 'Things':
        pass
    elif e.name == 'More Things':
        pass
     
def visualControlUpdate(state,batchdata):
    
    state.removeLastWP = False
    
    screenAreaTop = pygame.Rect(0,0,480,480)        # assign different areas of the screen for drawing (colours)
    screenAreaBottom = pygame.Rect(120,480, 240,240)
    screenOutOfBounds1 = pygame.Rect(360,480,120,360)
    screenOutOfBounds2 = pygame.Rect(0,480,120,360)
     

    
    """"
    for event in pygame.event.get():          # handle every event since the last frame.
        if event.type == pygame.QUIT:
            pygame.quit()       # quit the screen
            sys.exit()
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            pressPosition = (event.pos[0], event.pos[1])
            if (screenAreaTop.collidepoint(pressPosition)) or \
                (screenAreaBottom.collidepoint(pressPosition)):
                pressPosition = (event.pos[0], state.screenHeight - event.pos[1])
                state.waypoint = pressPosition
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            pressPosition = (event.pos[0], event.pos[1])      
            for index, r in enumerate(state.poleRecList, start = 0):
                if r.collidepoint(pressPosition):
                    state.poleList.pop(index)
                    state.poleRecList.pop(index)
                    print "waypoint removed..."
            print "You pressed at locaton: ", pressPosition
            state.removeLastWP = True
    """   
    for e in state.menu.handle_events(pygame.event.get()):
        if e.type == pygame.QUIT:
            pygame.quit()       # quit the screen
            sys.exit()
        elif e.type == MOUSEBUTTONDOWN and e.button ==1:
            pressPosition = (e.pos[0], e.pos[1])        # pin point press location
            if (screenAreaTop.collidepoint(pressPosition)) or \
                (screenAreaBottom.collidepoint(pressPosition)):
                pressPosition = (e.pos[0], state.screenHeight - e.pos[1])
                state.waypoint = pressPosition      # create new waypoint from press
            
        elif e.type == MOUSEBUTTONDOWN and e.button ==3:
            state.menu.show()     # show user menu
        elif e.type == USEREVENT:
            if e.code == 'MENU':
                handle_menu(e, state)

    state.screen.fill(GREY)         # fill the screen with colour
    state.screen.fill(GREEN, screenAreaTop)         # fill the screen with colour
    state.screen.fill(GREEN, screenAreaBottom)          # fill the screen with colour
    state.screen.fill(GREY, screenOutOfBounds1)         # fill the screen with colour
    state.screen.fill(GREY, screenOutOfBounds2)         # fill the screen with colour

    
    state.drawRobot(state.screen)       # draw the Robot to the screen
    state.drawObstacles(state.screen)   # draw the obstacles to the screen
    state.drawInfoPanel(state.screen )  # draw the information panel to the screen
    state.drawPath(state.scrBuff)       # draw the waypoints and path of the robot
    state.drawWaypoints(state.screen)
    state.checkForCollision()       # check for possible collision
    state.menu.draw()     # menu draw *test*
    pygame.display.update()      # update the screen
    
    for item in batchdata:      # process data from batchdata
        if item['messageType'] == 'robot':
            currentPos = (item['robotPos'])
            currentAngle = (item['robotAngle'])
            goalPos = (item['goal'])
            state.nearWaypoint = (item['nearWaypoint'])
            state.robotPos = (currentPos[0]/10.0, state.screenHeight -currentPos[1]/10.0)
            state.robotAngle = currentAngle
            state.targetPos = (goalPos[0]/10.0, state.screenHeight - goalPos[1]/10.0) 
            
        elif item['messageType'] == 'obstacle':
            state.barrierList = (item['barrierList'])        
            state.poleList = (item['poleList'])
            state.wallList = (item['wallList'])
            state.barrelList = (item['barrelList'])
            state.rampList = (item['rampList'])
            state.doorList = (item['doorList'])
            state.goalList = (item['goalList'])
            state.ballList = (item['ballList'])  
            
        elif item['messageType'] == 'stats':
            state.max = (item['max'])
            state.min = (item['min'])
            state.average = (item['average'])
            state.length = (item['length'])
            state.variance = (item['variance'])  
            
        elif item['messageType'] == 'scan':
            state.scanCone = (item['scanCone'])
            state.isCollision = (item['collision'])  
            
        elif item['messageType'] == 'control':
            state.rcFwd = abs((item['rcFwd']*127.0  ))
            state.rcTurn = abs((item['rcTurn']*127.0 ))
            
        elif item['messageType'] == 'odo':
            state.leftReading = (item['leftReading'])
            state.rightReading = (item['rightReading'])
            state.realMode = (item['mode'])
            
    if len(batchdata) == 0: return

def visualToRouteTranslator(sourceState, destState, destQueue):

    if sourceState.removeLastWP:
        destState.waypoints.pop()
        
        
    sourceState.waypointList = destState.waypoints
    if sourceState.waypoint != (0,0) and sourceState.waypoint != sourceState.prevWaypoint:
        sourceState.prevWaypoint = sourceState.waypoint
        message = {'messageType':'waypoint',
                   'newWaypoint'    :sourceState.waypoint,
                   'removeWaypoint' :sourceState.removeLastWP}
        destQueue.put(message)

def visualToAppManager(sourceState, destState, destQueue):
   # if sourceState.pauseLoops == True:
    message = {'messageType': 'pause',
                'pauseLoops': sourceState.pauseLoops}
    destQueue.put(message)
            
        