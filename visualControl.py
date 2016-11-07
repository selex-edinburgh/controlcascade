'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import pygame
import math
import sys
import os
import subprocess

from lib import *
from pygame import gfxdraw
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator
from pygame.locals import *
from lib.navigation import *

progname = sys.argv[0]      # lib import for right-click menu
progdir = os.path.dirname(progname)
sys.path.append(os.path.join(progdir,'lib'))
from popup_menu import NonBlockingPopupMenu


BLACK = (  0,   0,   0)     # global constants
WHITE = (255, 255, 255)
BLUE =  (  147,   179, 208)
LIGHT_BLUE = (120,135,171)
GREEN = (  34, 102,   102)
RED =   (192,   57,   43)
GREY = (52,73,94)
TRAIL_GREY = (34,167,240)
MARGIN = 200
DARK_GREY = (34,49,63)
ORANGE = (230,126,34)
SCREENWIDTH = 682      # set screen height and width
SCREENHEIGHT = 720
SCREENSCALE = 10       # set screen scaling amount (mm per pixel)
pygame.init()

menu_data = (
    'Main',
    'Remove Last Waypoint',
    (
        'Waypoint Type',
        'Waiting Waypoint',
        'Continuous Waypoint',
    ),
    'Remove Pole',
    (
        'Graphs',
        'Motor Graph',
        'Timing Graph',
    ),
    'Start (G)',
    'Stop (Spacebar)',
    'Quit (Escape)',
)

def scaleToScreen(D):           #scales to SCREENSCALE
    return int(D/SCREENSCALE)
    
def toScreenX(X):               #transform X coordinate to screen coordinate
    return int(scaleToScreen(X))
    
def toScreenY(Y):               #transform Y coordinate to screen coordinate
    return int(SCREENHEIGHT - scaleToScreen(Y))
    
def toScreenPos((X,Y)):         #transform X & Y coordinates to screen coordinates
    return((toScreenX(X),toScreenY(Y)))  

def scaleFromScreen(D):           #scales from SCREENSCALE
    return (D*SCREENSCALE)
    
def fromScreenX(X):               #transformscreen coordinate to X coordinate
    return scaleFromScreen(X)
    
def fromScreenY(Y):               #transformscreen coordinate to Y coordinate
    return scaleFromScreen(SCREENHEIGHT - Y)
    
def fromScreenPos((X,Y)):         #transform screen coordinates to X & Y coordinates
    return((fromScreenX(X),fromScreenY(Y)))

class VisualState(ObservableState):
    def __init__(self):
        super(VisualState,self).__init__()
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
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
        self.newWaypoint = WaypointManager.createWaypoint(0,0)       # temp waypoint when adding new waypoints to list
        self.newWaypointLast = self.newWaypoint       # previous waypoint
        self.robotPos = (0,0)       # current position of robot
        self.robotAngle = 0     # current angle of robot
        self.nextWaypoint = WaypointManager.createWaypoint(0,0)  # next waypoint
        self.waypointList = []  # list of waypoints
        self.scrBuff = None
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

        self.quitLoops = False      # initialized to false since do not want to quit at beginning
        self.stopLoops = True       # initialized to true to stop at beginning
        self.menu = NonBlockingPopupMenu(menu_data)      # define right-click menu

        self.eventPress = 0

        self.scanSensors = {} # add dictionary for sensorID's

    def drawRobot(self, surface):
        if self.scrBuff == None:
                self.scrBuff = surface.copy()
        surface.blit(self.scrBuff,(0,0))
        loc = self.image.get_rect().center
        rotImg = pygame.transform.rotate(self.image, 90.0 - self.robotAngle)
        rotImg.get_rect().center = loc

        surface.blit(rotImg, ((toScreenX(self.robotPos[0]) ) - rotImg.get_rect().width/2.0,
                              toScreenY(self.robotPos[1]) - rotImg.get_rect().height/2.0))
        for sensorID in self.scanSensors:
            pygame.draw.lines(surface, RED if self.scanSensors[sensorID][0] else BLACK , True, (toScreenPos(self.scanSensors[sensorID][1][1]), toScreenPos(self.scanSensors[sensorID][1][0]), toScreenPos(self.scanSensors[sensorID][1][2])), 2)
        
    def drawPath(self,surface):
        pygame.draw.circle(surface,BLACK,toScreenPos(self.nextWaypoint.getPosition()), scaleToScreen(40))                # draw the red dot on the current waypoint and previously met ones
        pygame.draw.line(surface,TRAIL_GREY,toScreenPos(self.robotPos),toScreenPos(self.robotPos), scaleToScreen(40))


    def drawWaypoints(self, surface):
        for w in self.waypointList:

            pygame.draw.circle(surface,WHITE,toScreenPos(w.getPosition()), scaleToScreen(40),)
            pygame.draw.circle(surface,BLACK,toScreenPos(w.getPosition()), scaleToScreen(40),2)

    def checkForCollision(self):
        self.poleRecList = []
        for p in self.poleList:
            poleRec = pygame.Rect(p[0] - 10, (SCREENHEIGHT - p[1] ) - 10 , 20,20)
            self.poleRecList.append(poleRec)

        chariotRec = pygame.Rect((self.robotPos[0] - 5, (SCREENHEIGHT - self.robotPos[1])+ 5), (65,65))

        for r in self.poleRecList:
            if chariotRec.colliderect(r):
                pass
                
    def drawObstacles(self,surface):
        for wall in self.wallList:      # draw the walls on the screen
            pygame.draw.line(surface, BLACK, toScreenPos((wall[0], wall[1])), toScreenPos((wall[2], wall[3])), 4 )

        for pole in self.poleList:      # draw poles on the screen
            poleTemp = toScreenPos(pole)
            pygame.draw.circle(surface,BLUE,poleTemp, 5,)
            pygame.draw.circle(surface,BLACK,poleTemp, 5, 2)

        for goal in self.goalList:
            pygame.draw.line(surface,BLACK,toScreenPos((goal[0],goal[1])),toScreenPos((goal[2],goal[3])), 4)

        for barrier in self.barrierList:
            pygame.draw.line(surface,BLACK,toScreenPos((barrier[0],barrier[1])),toScreenPos((barrier[2], barrier[3])), 2)
        for ball in self.ballList:
            ballTemp = toScreenPos(ball)
            pygame.draw.circle(surface,ORANGE,ballTemp, 7)
            pygame.draw.circle(surface,BLACK,ballTemp, 7, 1)
            
        pygame.draw.polygon(surface,BLACK,(toScreenPos((4800,7200)),toScreenPos((4420,7200)),toScreenPos((4800,6800))),0)     # corner of course
        pygame.draw.polygon(surface,BLACK,(toScreenPos((0,7200)),toScreenPos((420,7200)),toScreenPos((0,6800))),0)       # corner of course
        
    def drawExtras(self,surface):
        pygame.draw.line(surface,WHITE, (5, 500), (5, SCREENHEIGHT -5), 2)      # draw y axis
        surface.blit(self.font.render(("  North"), True, WHITE), (10,500))
        surface.blit(self.fontTitle.render(("Y"), True, WHITE), (10,600))

        pygame.draw.line(surface,WHITE, (5, SCREENHEIGHT - 5 ), (100, SCREENHEIGHT- 5), 2)      # draw x axis
        surface.blit(self.font.render(("East"), True, WHITE), (80,(SCREENHEIGHT - 22)))
        surface.blit(self.fontTitle.render(("X"), True, WHITE), (50,(SCREENHEIGHT - 22)))

        origin = pygame.Rect(-5,SCREENHEIGHT - 25, 40,40)
        pygame.draw.arc(surface, WHITE, origin, 0,2.2, 4)       # draw origin
    
        pygame.draw.line(surface,WHITE, (480, SCREENHEIGHT - 0 ), (480, SCREENHEIGHT- 10), 4) 
        pygame.draw.line(surface,WHITE, (0, SCREENHEIGHT - 710 ), (10, SCREENHEIGHT- 710), 4) 
        
    def distToPoint(self):
        a = (self.robotPos)
        b = (self.nextWaypoint.getPosition())
        return int(math.hypot(b[0] - a[0], b[1] - a[1]))        # find distance between the two points

    def drawInfoPanel(self,surface):
        surface.blit(self.fontTitle.render(("Robot Position"), True, WHITE), (505,(SCREENHEIGHT -710)))     # robotPos information panel
        surface.blit(self.font.render(("X,Y (mm):  ({0},{1})".format(int(self.robotPos[0]), int(self.robotPos[1]))), True, WHITE), (505,SCREENHEIGHT - 675))
        surface.blit(self.font.render(("Heading:   {0}".format(int(self.robotAngle))), True, WHITE), (505,SCREENHEIGHT -655))

        surface.blit(self.fontTitle.render(("Route"), True, WHITE), (505,(SCREENHEIGHT -600)))     # latency information panel
        surface.blit(self.font.render(("Next Waypoint:  ({0},{1})".format(int(self.nextWaypoint.getPosition()[0]), int(self.nextWaypoint.getPosition()[1]))), True, WHITE), (505,SCREENHEIGHT -565))
        surface.blit(self.font.render(("No. of Waypoints:  {0}".format(len(self.waypointList) -1)), True, WHITE), (505,SCREENHEIGHT -545))
        surface.blit(self.font.render(("Near Waypoint:            %s" % (self.nearWaypoint)), True, WHITE), (505,SCREENHEIGHT -525))
        surface.blit(self.font.render(("Distance to Waypoint:    %s" % (self.distToPoint())), True, WHITE), (505,SCREENHEIGHT -505))

        surface.blit(self.fontTitle.render(("Sensor"), True, WHITE), (505,(SCREENHEIGHT -475)))     # collision information panel
        if len(self.scanSensors) >= 1:
            displacement = 440
            for sensorID in self.scanSensors:
                surface.blit(self.font.render(("Obstacle in Range of %s: %s" % (sensorID, self.scanSensors[sensorID][0])), True, WHITE), (505,(SCREENHEIGHT -displacement)))
                displacement -= 20
        """
        surface.blit(self.fontTitle.render(("Motor"), True, WHITE), (505,(SCREENHEIGHT -390)))     # motor information panel
        surface.blit(self.font.render(("Turn Command: %s" % int((self.rcTurn))), True, WHITE), (505,(SCREENHEIGHT -355)))
        surface.blit(self.font.render(("Fwd Command: %s" % int((self.rcFwd))), True, WHITE), (505,(SCREENHEIGHT -335)))

        surface.blit(self.fontTitle.render(("Odometer"), True, WHITE), (505,(SCREENHEIGHT -285)))     # odometer information panel
        surface.blit(self.font.render(("Left Reading: %s" % int((self.leftReading))), True, WHITE), (505,(SCREENHEIGHT -240)))
        surface.blit(self.font.render(("Right Reading: %s" % int((self.rightReading))), True, WHITE), (505,(SCREENHEIGHT -220)))   # update the screen
        """
        surface.blit(self.fontTitle.render(("Main Loop Timing"), True, WHITE), (505,(SCREENHEIGHT -390)))     # latency information panel
        surface.blit(self.font.render(("Max (s):        {0:.3f}".format(self.maxLatency)), True, WHITE), (505,SCREENHEIGHT - 355))
        surface.blit(self.font.render(("Min (s):         {0:.3f}".format(self.minLatency)), True, WHITE), (505,SCREENHEIGHT -335))
        surface.blit(self.font.render(("Average (s):  {0:.3f}".format(self.averageLatency)), True, WHITE), (505,SCREENHEIGHT -315))
        surface.blit(self.font.render(("Msg Length:  {0}".format(self.lengthOfBatch)), True, BLUE), (505,SCREENHEIGHT -295))
        surface.blit(self.font.render(("Variance:       {0:.8f}".format(self.varianceOfLatency)), True, BLUE), (505,SCREENHEIGHT -275))

        if self.stopLoops:
            colour1 = BLUE
            colour2 = WHITE
        else:
            colour1 = WHITE
            colour2 = BLUE
        surface.blit(self.font.render(("Program Running"), True, colour1), (555, SCREENHEIGHT - 20))
        surface.blit(self.font.render(("Program Stopped"), True, colour2), (555, SCREENHEIGHT - 40))

        if WaypointManager.waypointType == WaypointTypeEnum.WAITING:
            colour1 = BLUE
            colour2 = WHITE
        else:
            colour1 = WHITE
            colour2 = BLUE   
        surface.blit(self.font.render(("Continuous WP"), True, colour1), (555, SCREENHEIGHT - 140))
        surface.blit(self.font.render(("Waiting WP"), True, colour2), (555, SCREENHEIGHT - 160))
        
        pos = fromScreenPos(pygame.mouse.get_pos())        # cursor position
        surface.blit(self.font.render(("Cursor pos:"),True, WHITE), (40, SCREENHEIGHT - 150))
        surface.blit(self.font.render(("{0}".format(pos)),True, WHITE), (40, SCREENHEIGHT - 130))
        if self.realMode:
            colour1 = BLUE
            colour2 = WHITE
        else:
            colour1 = WHITE
            colour2 = BLUE
        surface.blit(self.font.render(("Simulated mode"), True, colour1),(555,(SCREENHEIGHT - 100)))
        surface.blit(self.font.render(("Real mode"), True, colour2),(555,(SCREENHEIGHT - 80)))
        

def handle_menu(e, state):
    print 'Menu event: %s.%d: %s' % (e.name,e.item_id,e.text)

    if e.name is None:
        print 'Hide menu'
        state.menu.hide()
    elif e.name == 'Main':
        if e.text == 'Remove Last Waypoint':
            state.removeLastWP = True
        if e.text == 'Remove Pole':
            for index, r in enumerate(state.poleRecList, start = 0):
                if r.collidepoint(state.eventPress):
                    state.poleList.pop(index)
                    state.poleRecList.pop(index)
        if e.text == 'Start (G)':
            state.stopLoops = False
        if e.text == 'Stop (Spacebar)':
            state.stopLoops = True
        if e.text == 'Quit (Escape)':
            state.quitLoops = True
    elif e.name == 'Waypoint Type...':
        if e.text == 'Waiting Waypoint':
            WaypointManager.setWaypointType(WaypointTypeEnum.WAITING)
        if e.text == 'Continuous Waypoint':
            WaypointManager.setWaypointType(WaypointTypeEnum.CONTINUOUS)
            
    elif e.name == 'Graphs...':
        if e.text == 'Motor Graph':
            print 'started graphing'
            os.system('python graphs/motorGraph.py')
            print "motorororooro"
        if e.text == 'Timing Graph':
            os.system('python graphs/statsGraph.py')
            print "motorororooro"
    elif e.name == 'More Things':
        
        pass

def visualControlUpdate(state,batchdata):
    if state.quitLoops:  return
    state.removeLastWP = False
    screenAreaTop = pygame.Rect(0,0,480,480)        # assign different areas of the screen for drawing (colours)
    screenAreaBottom = pygame.Rect(120,480, 240,240)
    screenOutOfBounds1 = pygame.Rect(360,480,120,360)
    screenOutOfBounds2 = pygame.Rect(0,480,120,360)

    for e in state.menu.handle_events(pygame.event.get()):
        if e.type == MOUSEBUTTONDOWN and e.button ==1:
            pressPosition = (e.pos[0], e.pos[1])        # sets screen coordinates to MouseButtonDown coordinates
            if (screenAreaTop.collidepoint(pressPosition)) or \
                  (screenAreaBottom.collidepoint(pressPosition)): # detect if click is within the arena/visual screen
                state.newWaypoint = WaypointManager.createWaypoint(fromScreenX(e.pos[0]), fromScreenY(e.pos[1]))      # create new temp waypoint position from arena coordinates
        elif e.type == MOUSEBUTTONUP and e.button ==3:
             state.menu.show()     # show user menu
             state.eventPress = (e.pos[0], e.pos[1])
        elif e.type == USEREVENT:
            if e.code == 'MENU':
                handle_menu(e, state)       
        elif e.type == KEYDOWN and e.key == K_SPACE:
            state.stopLoops = True
        elif e.type == KEYDOWN and e.key == K_g:
            state.stopLoops = False
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            state.quitLoops = True
            
    if state.quitLoops:
        pygame.quit()
        return
    
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
    state.drawExtras(state.screen)      # draw the extra misc. information
    state.checkForCollision()       # check for possible collision
    state.menu.draw()     # menu draw *test*
    pygame.display.update()      # update the screen

    for item in batchdata:      # process data from batchdata
        if item['messageType'] == 'robot':
            currentPos = (item['robotPos'])
            currentAngle = (item['robotAngle'])
            state.nextWaypoint = (item['nextWaypoint'])
            state.nearWaypoint = (item['nearWaypoint'])
            state.robotPos = currentPos
            state.robotAngle = currentAngle

        elif item['messageType'] == 'waypointList':
            state.waypointList = (item['waypointList'])

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
            state.maxLatency = (item['max'])
            state.minLatency = (item['min'])
            state.averageLatency = (item['average'])
            state.lengthOfBatch = (item['length'])
            state.varianceOfLatency = (item['variance'])
        elif item['messageType'] == 'scan':
            state.scanSensors[item['sensorID']] = [item['collision'], item['scanCone']]
            
        elif item['messageType'] == 'control':
            state.rcFwd = abs((item['rcFwd']*127.0  ))
            state.rcTurn = abs((item['rcTurn']*127.0 ))

        elif item['messageType'] == 'odo':
            state.leftReading = (item['leftReading'])
            state.rightReading = (item['rightReading'])
            state.realMode = (item['mode'])

    if len(batchdata) == 0: return


def visualToRouteTranslator(sourceState, destState, destQueue):

    if len(sourceState.waypointList) >= 1:    
        if destState.nearWaypoint and sourceState.nextWaypoint == sourceState.waypointList[-1]:       # stop if at last waypoint
            sourceState.stopLoops = True

    if sourceState.newWaypoint != sourceState.newWaypointLast:
        sourceState.newWaypointLast = sourceState.newWaypoint
        message = {'messageType':'newWaypoint',
                   'newWaypoint'    :sourceState.newWaypoint}
        destQueue.put(message)

    if sourceState.removeLastWP == True:
        message = {'messageType':'removeWaypoint'}
        destQueue.put(message)

def visualToStartStop(sourceState, destState, destQueue):

    message = {'messageType': 'loopControlMessage',
                'stopLoops': sourceState.stopLoops,
                'quitLoops': sourceState.quitLoops}
    destQueue.put(message)

def visualToQuit(sourceState, destState, destQueue):

    if sourceState.quitLoops:
        message = {'messageType': 'loopControlMessage',
                   'stopLoops': sourceState.stopLoops,
                   'quitLoops': sourceState.quitLoops}
        destQueue.put(message)
    

