import pygame
import math
from  pygame import gfxdraw
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

BLACK = (  0,   0,   0)     # global constants
WHITE = (255, 255, 255) 
BLUE =  (  0,   0, 255)
GREEN = (  20, 150,   0, 128)
RED =   (255,   0,   0)
GREY = (205,201,201)
MARGIN = 200
pygame.init()

class VisualState(ObservableState):
    def __init__(self):
        super(VisualState,self).__init__()
        
        self.screenWidth = 682      # set screen height and width
        self.screenHeight = 720
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))       
        pygame.display.set_caption('Rampyge')       # screen caption        
        self.font = pygame.font.SysFont('Arial', 16)        # different fonts used in the program
        self.fontTitle = pygame.font.SysFont('Arial',22)                 
        self.image = pygame.image.load('images/Tank.gif')       # robot image      
        self.wallList = []      # enviromentals
        self.poleList = []
        self.poleRecList = []       # used for collision detection
        self.waypoint = (0,0)       # list of waypoints       
        self.robotPos = (0,0)       # current position of robot
        self.robotAngle = 0     # current angle of robot
        self.targetPos = (0,0)      # next waypoint      
        self.prevWaypoint = (0,0)       # previous waypoints              
        self.scrBuff = None        
        self.scanCone = ((0,0),(0,0),(0.0))     # scan used for collison range
        self.isCollision = False    # bool to check if pole in collision range        
        self.removeLastWP = False       
        self.rcFwd = 0      #information panel data for motors
        self.rcTurn = 0        
        self.leftReading = 0        #information panel data for odometers
        self.rightReading = 0     
        self.maxLatency = 0       #information panel data for control loops
        self.minLatency = 0
        self.averageLatency = 0
        self.lengthOfBatch = 0
        self.varianceOfLatency = 0

    def run_once(f):
        def wrapper(*args, **kwargs):
            if not wrapper.has_run:
                wrapper.has_run = True
                return f(*args, **kwargs)
        wrapper.has_run = False
        return wrapper 
        
    def drawRobot(self, surface):
        surface.blit(self.scrBuff,(0,0))
        
        loc = self.image.get_rect().center
        rotImg = pygame.transform.rotate(self.image, 90.0 - self.robotAngle)
        pygame.draw.line(self.scrBuff,BLACK, self.robotPos,self.robotPos, 4)
        pygame.draw.circle(self.scrBuff,RED,(int(self.targetPos[0] ), int(self.targetPos[1])), 4)
        rotImg.get_rect().center = loc
        
        surface.blit(rotImg, ((self.robotPos[0] ) - rotImg.get_rect().width/2.0,
                              self.robotPos[1] - rotImg.get_rect().height/2.0))
        
        pygame.display.update()      # update the screen
        if self.isCollision == False:
            pygame.draw.aalines(self.screen, BLACK, True, ((self.scanCone[0]), self.scanCone[1], self.scanCone[2]))
        else:
            pygame.draw.aalines(self.screen, RED, True, ((self.scanCone[0]), self.scanCone[1], self.scanCone[2]))


    def checkForCollision(self):
        self.poleRecList = []
        for p in self.poleList:
            poleRec = pygame.Rect(p[0] + 5, (self.screenHeight - p[1] ) -5, 40,40)
            self.poleRecList.append(poleRec)

        chariotRec = pygame.Rect((self.robotPos[0] - 5, (self.screenHeight - self.robotPos[1])+ 5), (65,65)) 

        for r in self.poleRecList:
            if chariotRec.colliderect(r):
                pass
            
    def drawObstacles(self,surface):
        if self.scrBuff == None:
            self.scrBuff = surface.copy()
        surface.blit(self.scrBuff,(0,0))    
        pygame.draw.circle(self.scrBuff,WHITE,(self.waypoint[0], self.screenHeight - self.waypoint[1]), 4,)     # draw the waypoints
        pygame.draw.circle(self.scrBuff,BLACK,(self.waypoint[0], self.screenHeight - self.waypoint[1]), 4, 2)
                    
        for wall in self.wallList:      # draw the walls on the screen
            self.wall = (wall[0], self.screenHeight - wall[1],  wall[2], self.screenHeight - wall[3])
            pygame.draw.line(self.scrBuff, BLACK, (self.wall[0], self.wall[1]), (self.wall[2], self.wall[3]), 4 )
            
        for pole in self.poleList:      # draw poles on the screen
            self.pole = ( pole[0], self.screenHeight - pole[1])
            pygame.draw.circle(self.scrBuff,BLUE,self.pole, 10,)
            pygame.draw.circle(self.scrBuff,BLACK,self.pole, 10, 2)
        pygame.display.update() 
    def drawInfoPanel(self,surface):
 
        self.screen.blit(self.fontTitle.render(("Positional Data"), True, BLACK), (505,(721 -710)))     # robotPos information panel
        self.screen.blit(self.font.render(("Position: ({0},{1})".format(int(self.robotPos[0]), self.screenHeight - int(self.robotPos[1]))), True, BLACK), (505,721 -675))
        self.screen.blit(self.font.render(("Angle: (Deg): {0}".format(int(self.robotAngle))), True, BLACK), (505,721 -655))
        self.screen.blit(self.font.render(("Angle: (Rad): {0:.2f}".format(math.radians(self.robotAngle))), True, BLACK), (505,721 -635))
        self.screen.blit(self.font.render(("Target: ({0},{1})".format(int(self.targetPos[0]), self.screenHeight - int(self.targetPos[1]))), True, BLACK), (505,721 -615))
        
        self.screen.blit(self.fontTitle.render(("Latency Data"), True, BLACK), (505,(721 -555)))     # latency information panel
        self.screen.blit(self.font.render(("Max (s):        {0:.3f}".format(self.maxLatency)), True, BLACK), (505,721 -520))
        self.screen.blit(self.font.render(("Min (s):         {0:.3f}".format(self.minLatency)), True, BLACK), (505,721 -500))
        self.screen.blit(self.font.render(("Average (s):  {0:.3f}".format(self.averageLatency)), True, BLACK), (505,721 -480))
        self.screen.blit(self.font.render(("Msg Length:  {0}".format(self.lengthOfBatch)), True, BLACK), (505,721 -460))
        self.screen.blit(self.font.render(("Variance:       {0:.3f}".format(self.varianceOfLatency)), True, BLACK), (505,721 -440))
        
        self.screen.blit(self.fontTitle.render(("Collision Data"), True, BLACK), (505,(721 -400)))     # collision information panel
        self.screen.blit(self.font.render(("In Range: %s" % (self.isCollision)), True, BLACK), (505,(721 -365)))

        self.screen.blit(self.fontTitle.render(("Motor Data"), True, BLACK), (505,(721 -305)))     # latency information panel
        self.screen.blit(self.font.render(("Fwd Command: %s" % int((self.rcFwd))), True, BLACK), (505,(721 -270)))
        self.screen.blit(self.font.render(("Turn Command: %s" % int((self.rcTurn))), True, BLACK), (505,(721 -250)))
        
        self.screen.blit(self.fontTitle.render(("Odometer Data"), True, BLACK), (505,(721 -190)))     # latency information panel
        self.screen.blit(self.font.render(("Left Reading: %s" % int((self.leftReading))), True, BLACK), (505,(721 -155)))
        self.screen.blit(self.font.render(("Right Reading: %s" % int((self.rightReading))), True, BLACK), (505,(721 -135)))
        pygame.display.update()      # update the screen
        
        
def visualControlUpdate(state,batchdata):
    
    state.removeLastWP = False
    for event in pygame.event.get():          # handle every event since the last frame.
        if event.type == pygame.QUIT:
            pygame.quit()       # quit the screen
            sys.exit()
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            pressPosition = (event.pos[0], event.pos[1])      
            for index, r in enumerate(state.poleRecList, start = 0):
                if r.collidepoint(pressPosition):
                    state.poleList.pop(index)
                    state.poleRecList.pop(index)
                    print len(state.poleList)
            print "You pressed at locaton: ", pressPosition
            pressPosition = (event.pos[0], state.screenHeight - event.pos[1])
            state.waypoint = pressPosition
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            print "Right click"
            state.removeLastWP = True

    screenAreaTop = pygame.Rect(0,0,480,480)        # assign different areas of the screen for drawing (colours)
    screenAreaBottom = pygame.Rect(120,480, 240,240)
    screenOutOfBounds1 = pygame.Rect(360,480,120,360)
    screenOutOfBounds2 = pygame.Rect(0,480,120,360)

    state.screen.fill(GREY) 
    state.screen.fill(GREEN, screenAreaTop)
    state.screen.fill(GREEN, screenAreaBottom) 
    state.screen.fill(GREY, screenOutOfBounds1)
    state.screen.fill(GREY, screenOutOfBounds2)

    
    state.drawObstacles(state.screen)       # draw the obstacles to the screen
    state.drawRobot(state.screen)       # draw the Robot to the screen
    state.drawInfoPanel(state.scrBuff )     # draw the information panel to the screen
    state.checkForCollision()       # check for possible collision
    
    for item in batchdata:      # process data from batchdata
        if item['messageType'] == 'robot':
            currentPos = (item['robotPos'])
            currentAngle = (item['robotAngle'])
            goalPos = (item['goal'])
            state.robotPos = (currentPos[0]/10.0, state.screenHeight -currentPos[1]/10.0)
            state.robotAngle = currentAngle
            state.targetPos = (goalPos[0]/10.0, state.screenHeight - goalPos[1]/10.0) 
            
        elif item['messageType'] == 'obstacle':  
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
            
    if len(batchdata) == 0: return

def visualToRouteTranslator(sourceState, destState, destQueue):
    if sourceState.waypoint != (0,0) and sourceState.waypoint != sourceState.prevWaypoint:
        sourceState.prevWaypoint = sourceState.waypoint
        message = {'messageType':'waypoint',
                   'newWaypoint'    :sourceState.waypoint,
                   'removeWaypoint' :sourceState.removeLastWP}
        destQueue.put(message)
