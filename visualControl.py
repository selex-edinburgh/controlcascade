import pygame
import math

from  pygame import gfxdraw
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

"""
GLOBAL CONSTANTS
"""
BLACK = (  0,   0,   0)
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
        pygame.display.set_caption('Rampyge')
        self.screenWidth = 682 # +400
        self.screenHeight = 721 
        self.font = pygame.font.SysFont('Arial', 16)
        self.fontTitle = pygame.font.SysFont('Arial',22)
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        self.img_path = 'images/Tank.gif'
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((20, 150, 0))   
        
        self.transScreen = pygame.Surface((self.screenWidth, self.screenHeight), pygame.SRCALPHA, 32)
        self.transScreen =  self.transScreen.convert_alpha()
        
        
        self.clock = pygame.time.Clock()
        self.wallList = []
        self.poleList = []
        self.image = pygame.image.load(self.img_path)
        self.pos = (0,0)
        self.angle = 0
        self.targetPos = (0,0)
        self.waypoint = (0,0)
        self.prevWaypoint = (0,0)
        self.scrBuff = None
        self.poleRecList = []
        
        self.rcFwd = 0
        self.rcTurn = 0
        
        self.max = 0
        self.min = 0
        self.average = 0
        self.length = 0
        self.variance = 0
        self.isCollision = False
        self.removeLastWP = False
        self.scanCone = ((0,0),(0,0),(0.0))
    def drawRobot(self, surface):
        surface.blit(self.scrBuff,(0,0))
        # blit yourself at your current position
        loc = self.image.get_rect().center
        rotImg = pygame.transform.rotate(self.image, 90.0 - self.angle)
        pygame.draw.line(self.scrBuff,BLACK, self.pos,self.pos, 4)
        pygame.draw.circle(self.scrBuff,RED,(int(self.targetPos[0] ), int(self.targetPos[1])), 4)
        rotImg.get_rect().center = loc
        
        surface.blit(rotImg, ((self.pos[0] ) - rotImg.get_rect().width/2.0,
                              self.pos[1] - rotImg.get_rect().height/2.0))
        
        pygame.display.update()      # update the screen
        if self.isCollision == False:
            #pygame.draw.line(self.screen, BLACK, ((self.scanCone[0]), self.scanCone[1], self.scanCone[2]), 1)
            pass
        else:
            #pygame.draw.line(self.screen, RED, ((self.scanCone[0]), self.scanCone[1], self.scanCone[2]), 1)
            pass

        
    def checkForCollision(self):
        for p in self.poleList:
            poleRec = pygame.Rect(p[0] + 5, (self.screenHeight - p[1] ) -5, 40,40)

            #self.poleRecList.append(poleRec)

        chariotRec = pygame.Rect((self.pos[0] - 5, (self.screenHeight - self.pos[1])+ 5), (65,65)) 

        for r in self.poleRecList:
            if chariotRec.colliderect(r):
                #print "collision"
                pass
         
         
    def drawObstacles(self,surface):
        if self.scrBuff == None:
            self.scrBuff = surface.copy()

                
        pygame.draw.circle(self.scrBuff,WHITE,(self.waypoint[0], self.screenHeight - self.waypoint[1]), 4,)
        pygame.draw.circle(self.scrBuff,BLACK,(self.waypoint[0], self.screenHeight - self.waypoint[1]), 4, 2)
                    
        for wall in self.wallList:
            self.wall = (wall[0], self.screenHeight - wall[1],  wall[2], self.screenHeight - wall[3])
            pygame.draw.line(self.scrBuff, BLACK, (self.wall[0], self.wall[1]), (self.wall[2], self.wall[3]), 4 )
            
        for pole in self.poleList:
            self.pole = ( pole[0], self.screenHeight - pole[1])
            pygame.draw.circle(self.scrBuff,BLUE,self.pole, 10,)
            pygame.draw.circle(self.scrBuff,BLACK,self.pole, 10, 2)
       
    def drawInfoPanel(self,surface):
 
        self.screen.blit(self.fontTitle.render(("Positional Data"), True, BLACK), (505,(721 -710)))     # pos information panel
        self.screen.blit(self.font.render(("Position: ({0},{1})".format(int(self.pos[0]), self.screenHeight - int(self.pos[1]))), True, BLACK), (505,721 -675))
        self.screen.blit(self.font.render(("Angle (Deg): {0}".format(int(self.angle))), True, BLACK), (505,721 -655))
        self.screen.blit(self.font.render(("Angle (Rad): {0:.2f}".format(math.radians(self.angle))), True, BLACK), (505,721 -635))
        self.screen.blit(self.font.render(("Target: ({0},{1})".format(int(self.targetPos[0]), self.screenHeight - int(self.targetPos[1]))), True, BLACK), (505,721 -615))
        
        self.screen.blit(self.fontTitle.render(("Latency Data"), True, BLACK), (505,(721 -555)))     # latency information panel
        self.screen.blit(self.font.render(("Max (s):        {0:.3f}".format(self.max)), True, BLACK), (505,721 -520))
        self.screen.blit(self.font.render(("Min (s):         {0:.3f}".format(self.min)), True, BLACK), (505,721 -500))
        self.screen.blit(self.font.render(("Average (s):  {0:.3f}".format(self.average)), True, BLACK), (505,721 -480))
        self.screen.blit(self.font.render(("Msg Length:  {0}".format(self.length)), True, BLACK), (505,721 -460))
        self.screen.blit(self.font.render(("Variance:       {0:.3f}".format(self.variance)), True, BLACK), (505,721 -440))
        
        self.screen.blit(self.fontTitle.render(("Collision Data"), True, BLACK), (505,(721 -400)))     # collision information panel
        self.screen.blit(self.font.render(("In Range: %s" % (self.isCollision)), True, BLACK), (505,(721 -365)))

        self.screen.blit(self.fontTitle.render(("Motor Data"), True, BLACK), (505,(721 -305)))     # latency information panel
        self.screen.blit(self.font.render(("Fwd Command: %s" % (self.rcFwd)), True, BLACK), (505,(721 -270)))
        self.screen.blit(self.font.render(("Turn Command: %s" % (self.rcTurn)), True, BLACK), (505,(721 -250)))
        
        pygame.display.update()      # update the screen
        
        
def visualControlUpdate(state,batchdata):
    
    state.removeLastWP = False
    for event in pygame.event.get():          # handle every event since the last frame.
        if event.type == pygame.QUIT:
            pygame.quit()       # quit the screen
            sys.exit()
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            pos = (event.pos[0],  state.screenHeight - event.pos[1])

            print "You pressed at locaton: ", pos
            state.waypoint = pos
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            print "Right click"
            state.removeLastWP = True

    scrBackground = pygame.Rect(0,0,480,480)
    scrBackgroundBottom = pygame.Rect(120,480, 240,240)
    scrBlockade = pygame.Rect(360,480,120,360)
    scrBlockade2 = pygame.Rect(0,480,120,360)
    state.screen.fill(GREY) 
    state.screen.fill(GREEN, scrBackground) # fill the screen with white
    state.screen.fill(GREEN, scrBackgroundBottom) # fill the screen with white
    state.screen.fill(GREY, scrBlockade)
    state.screen.fill(GREY, scrBlockade2)
    state.drawObstacles(state.screen)
    state.drawRobot(state.screen) # draw the Robot to the screen
    state.drawInfoPanel(state.scrBuff )
    state.checkForCollision()
    

    for item in batchdata:
    
        if item['messageType'] == 'robot':
            currentPos = (item['robotPos'])
            currentAngle = (item['robotAngle'])
            demandPos = (item['demandPos'])
            state.pos = (currentPos[0]/10.0, state.screenHeight -currentPos[1]/10.0)
            state.angle = currentAngle
            state.targetPos = (demandPos[0]/10.0, state.screenHeight - demandPos[1]/10.0) 
            #self.targetAngle =  state.demandAngle #/ math.pi * 180.0
            
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
            state.rcFwd = (item['rcFwd']*127.0  + 1.0)
            state.rcTurn = (item['rcTurn']*127.0 + 1.0)
    if len(batchdata) == 0: return

def visualToRouteTranslator(sourceState, destState, destQueue):
    if sourceState.waypoint != (0,0) and sourceState.waypoint != sourceState.prevWaypoint:
        sourceState.prevWaypoint = sourceState.waypoint
        message = {'messageType':'waypoint',
                   'newWaypoint'    :sourceState.waypoint,
                   'removeWaypoint' :sourceState.removeLastWP}
        destQueue.put(message)


        
