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
pygame.init()

menu_data = (
    'Main',
    'Remove Last Waypoint',
    'Waiting Waypoint',
    'Continuous Waypoint',
    'Stop',
    'Start',
    'Remove Pole',
    'Timing Graph',
    'Motor Graph',
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
        self.waypoint = (0,0)       # temp waypoint when adding new waypoints to list
        self.robotPos = (0,0)       # current position of robot
        self.robotAngle = 0     # current angle of robot
        self.targetPos = (0,0)      # next waypoint
        self.prevWaypoint = (0,0)       # previous waypoints
        self.waypointList = []  # list of waypoints
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

        self.stopLoops = True       # initialized to true to stop at beginning
        self.waitLoops = False       # initialized to false since will be stopped at beginning so no point in wait in wait
        self.menu = NonBlockingPopupMenu(menu_data)      # define right-click menu

        self.eventPress = 0

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
            pygame.draw.circle(surface,BLUE,self.pole, 5,)
            pygame.draw.circle(surface,BLACK,self.pole, 5, 2)

        for goal in self.goalList:
            self.goal = (goal[0], self.screenHeight - goal[1], goal[2], self.screenHeight - goal[3])
            pygame.draw.line(surface,BLACK,(self.goal[0],self.goal[1]),(self.goal[2],self.goal[3]), 4)

        for barrier in self.barrierList:
            self.barrier = (barrier[0], self.screenHeight - barrier[1], barrier[2], self.screenHeight - barrier[3])
            pygame.draw.line(surface,BLACK,(self.barrier[0],self.barrier[1]),(self.barrier[2], self.barrier[3]), 2)
        for ball in self.ballList:
            self.ball = (ball[0], self.screenHeight - ball[1])
            pygame.draw.circle(surface,ORANGE,self.ball, 7)
            pygame.draw.circle(surface,BLACK,self.ball, 7, 1)
            
        pygame.draw.polygon(surface,BLACK,((480,0),(442,0),(480,40)),0)     # corner of course
        pygame.draw.polygon(surface,BLACK,((0,0),(42,0),(0,40)),0)       # corner of course
        
    def drawExtras(self,surface):
        pygame.draw.line(surface,WHITE, (5, 500), (5, self.screenHeight -5), 2)      # draw y axis
        surface.blit(self.font.render(("  North"), True, WHITE), (10,500))
        surface.blit(self.fontTitle.render(("Y"), True, WHITE), (10,600))

        pygame.draw.line(surface,WHITE, (5, self.screenHeight - 5 ), (100, self.screenHeight- 5), 2)      # draw x axis
        surface.blit(self.font.render(("East"), True, WHITE), (80,(self.screenHeight - 22)))
        surface.blit(self.fontTitle.render(("X"), True, WHITE), (50,(self.screenHeight - 22)))

        origin = pygame.Rect(-5,self.screenHeight - 25, 40,40)
        pygame.draw.arc(surface, WHITE, origin, 0,2.2, 4)       # draw origin
    
        pygame.draw.line(surface,WHITE, (480, self.screenHeight - 0 ), (480, self.screenHeight- 10), 4) 
        pygame.draw.line(surface,WHITE, (0, self.screenHeight - 710 ), (10, self.screenHeight- 710), 4) 
        
    def distToPoint(self):
        a = (self.robotPos)
        b = (self.targetPos)
        return int(math.hypot(b[0] - a[0], b[1] - a[1]))        # find distance between the two points

    def drawInfoPanel(self,surface):
        surface.blit(self.fontTitle.render(("Robot Position"), True, WHITE), (505,(self.screenHeight -710)))     # robotPos information panel
        surface.blit(self.font.render(("X,Y (mm):  ({0},{1})".format(int(self.robotPos[0]), self.screenHeight - int(self.robotPos[1]))), True, WHITE), (505,self.screenHeight - 675))
        surface.blit(self.font.render(("Heading:   {0}".format(int(self.robotAngle))), True, WHITE), (505,self.screenHeight -655))

        surface.blit(self.fontTitle.render(("Route"), True, WHITE), (505,(self.screenHeight -600)))     # latency information panel
        surface.blit(self.font.render(("Next Waypoint:  ({0},{1})".format(int(self.targetPos[0]), self.screenHeight - int(self.targetPos[1]))), True, WHITE), (505,self.screenHeight -565))
        surface.blit(self.font.render(("No. of Waypoints:  {0}".format(len(self.waypointList) -1)), True, WHITE), (505,self.screenHeight -545))
        surface.blit(self.font.render(("Near Waypoint:            %s" % (self.nearWaypoint)), True, WHITE), (505,self.screenHeight -525))
        surface.blit(self.font.render(("Distance to Waypoint:    %s" % (self.distToPoint())), True, WHITE), (505,self.screenHeight -505))

        surface.blit(self.fontTitle.render(("Sensor"), True, WHITE), (505,(self.screenHeight -475)))     # collision information panel
        surface.blit(self.font.render(("Obstacle in Range: %s" % (self.isCollision)), True, WHITE), (505,(self.screenHeight -440)))
        """
        surface.blit(self.fontTitle.render(("Motor"), True, WHITE), (505,(self.screenHeight -390)))     # motor information panel
        surface.blit(self.font.render(("Turn Command: %s" % int((self.rcTurn))), True, WHITE), (505,(self.screenHeight -355)))
        surface.blit(self.font.render(("Fwd Command: %s" % int((self.rcFwd))), True, WHITE), (505,(self.screenHeight -335)))

        surface.blit(self.fontTitle.render(("Odometer"), True, WHITE), (505,(self.screenHeight -285)))     # odometer information panel
        surface.blit(self.font.render(("Left Reading: %s" % int((self.leftReading))), True, WHITE), (505,(self.screenHeight -240)))
        surface.blit(self.font.render(("Right Reading: %s" % int((self.rightReading))), True, WHITE), (505,(self.screenHeight -220)))   # update the screen
        """
        surface.blit(self.fontTitle.render(("Main Loop Timing"), True, WHITE), (505,(self.screenHeight -390)))     # latency information panel
        surface.blit(self.font.render(("Max (s):        {0:.3f}".format(self.maxLatency)), True, WHITE), (505,self.screenHeight - 355))
        surface.blit(self.font.render(("Min (s):         {0:.3f}".format(self.minLatency)), True, WHITE), (505,self.screenHeight -335))
        surface.blit(self.font.render(("Average (s):  {0:.3f}".format(self.averageLatency)), True, WHITE), (505,self.screenHeight -315))
        surface.blit(self.font.render(("Msg Length:  {0}".format(self.lengthOfBatch)), True, BLUE), (505,self.screenHeight -295))
        surface.blit(self.font.render(("Variance:       {0:.8f}".format(self.varianceOfLatency)), True, BLUE), (505,self.screenHeight -275))

        if self.stopLoops:
            surface.blit(self.font.render(("Program Running"), True, BLUE), (555, self.screenHeight - 20))
            surface.blit(self.font.render(("Program Stopped"), True, WHITE), (555, self.screenHeight - 40))
        else:
            surface.blit(self.font.render(("Program Stopped"), True, BLUE), (555, self.screenHeight - 40))
            surface.blit(self.font.render(("Program Running"), True, WHITE), (555, self.screenHeight - 20))

        if self.waitLoops:
            surface.blit(self.font.render(("Continuous WP"), True, BLUE), (555, self.screenHeight - 140))
            surface.blit(self.font.render(("Waiting WP"), True, WHITE), (555, self.screenHeight - 160))
        else:
            surface.blit(self.font.render(("Waiting WP"), True, BLUE), (555, self.screenHeight - 160))
            surface.blit(self.font.render(("Continuous WP"), True, WHITE), (555, self.screenHeight - 140))
        
        pos = pygame.mouse.get_pos()        # cursor position
        pos = (pos[0], self.screenHeight - pos[1] )
        surface.blit(self.font.render(("Cursor pos:"),True, WHITE), (40, self.screenHeight - 150))
        surface.blit(self.font.render(("{0}".format(pos)),True, WHITE), (40, self.screenHeight - 130))
        if self.realMode:
            surface.blit(self.font.render(("Real mode"), True, WHITE),(555,(self.screenHeight - 80)))
            surface.blit(self.font.render(("Simulated mode"), True, BLUE),(555,(self.screenHeight - 100)))
        else:
            surface.blit(self.font.render(("Simulated mode"), True, WHITE),(555,(self.screenHeight - 100)))
            surface.blit(self.font.render(("Real mode"), True, BLUE),(555,(self.screenHeight - 80)))

def handle_menu(e, state):
    print 'Menu event: %s.%d: %s' % (e.name,e.item_id,e.text)

    if e.name is None:
        print 'Hide menu'
        state.menu.hide()
    elif e.name == 'Main':
        if e.text == 'Quit':
            pygame.quit()
        if e.text == 'Stop':
            state.stopLoops = True
        if e.text == 'Start':
            state.stopLoops = False
        if e.text == 'Waiting Waypoint':
            state.waitLoops = True
        if e.text == 'Continuous Waypoint':
            state.waitLoops = False
        if e.text == 'Remove Last Waypoint':
            state.removeLastWP = True
        if e.text == 'Remove Pole':
            for index, r in enumerate(state.poleRecList, start = 0):
                if r.collidepoint(state.eventPress):
                    state.poleList.pop(index)
                    state.poleRecList.pop(index)
        if e.text == 'Motor Graph':
            subprocess.Popen(['sh', 'runMotorGraphPy.sh'])
            print "motorororooro"
        if e.text == 'Timing Graph':
            subprocess.Popen(['sh', 'runStatsGraphPy.sh'])
            print "motorororooro"
            
    elif e.name == 'Graphs':
        if e.text == 'Motor Graph':
            os.system('py motorGraph.py')
            print "motorororooro"
        if e.text == 'Timing Graph':
            os.system('statsGraph.py')
            print "motorororooro"
    elif e.name == 'More Things':
        
        pass

def visualControlUpdate(state,batchdata):
    state.removeLastWP = False
    screenAreaTop = pygame.Rect(0,0,480,480)        # assign different areas of the screen for drawing (colours)
    screenAreaBottom = pygame.Rect(120,480, 240,240)
    screenOutOfBounds1 = pygame.Rect(360,480,120,360)
    screenOutOfBounds2 = pygame.Rect(0,480,120,360)

    try:
        if state.targetPos == state.waypointList[-1]:
            state.stopLoops = True
    except:
        print "error"

    for e in state.menu.handle_events(pygame.event.get()):
        if e.type == pygame.QUIT:
            pygame.quit()       # quit the screen
            sys.exit()
        elif e.type == MOUSEBUTTONDOWN and e.button ==1:
            pressPosition = (e.pos[0], e.pos[1])        # sets screen coordinates to MouseButtonDown coordinates
            if (screenAreaTop.collidepoint(pressPosition)) or \
                (screenAreaBottom.collidepoint(pressPosition)): # detect if click is within the arena/visual screen
                pressPosition = (e.pos[0], state.screenHeight - e.pos[1]) # converts screen coordinates to arena coordinates
                state.waypoint = pressPosition      # create new waypoint from arena coordinates
        elif e.type == MOUSEBUTTONDOWN and e.button ==3:
            state.menu.show()     # show user menu
            state.eventPress = (e.pos[0], e.pos[1])
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
    state.drawExtras(state.screen)      # draw the extra misc. information
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
            state.maxLatency = (item['max'])
            state.minLatency = (item['min'])
            state.averageLatency = (item['average'])
            state.lengthOfBatch = (item['length'])
            state.varianceOfLatency = (item['variance'])
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

    sourceState.waypointList = destState.waypoints
    if sourceState.removeLastWP:
        destState.waypoints.pop()

    a = (sourceState.waypointList[-1][0] / 10, (sourceState.screenHeight - (sourceState.waypointList[-1][1] /10)))
    b = sourceState.targetPos[0], sourceState.targetPos[1]
    if destState.nearWaypoint and b == a:       # stop if at last waypoint
        sourceState.stopLoops = True

    if sourceState.waypoint != (0,0) and sourceState.waypoint != sourceState.prevWaypoint:
        sourceState.prevWaypoint = sourceState.waypoint
        message = {'messageType':'waypoint',
                   'newWaypoint'    :sourceState.waypoint,
                   'removeWaypoint' :sourceState.removeLastWP}
        destQueue.put(message)

def visualToAppManager(sourceState, destState, destQueue):
   # if sourceState.stopLoops == True:
    message = {'messageType': 'stop',
                'stopLoops': sourceState.stopLoops}
    destQueue.put(message)
