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
GREEN = (  20, 150,   0)
RED =   (255,   0,   0)
pygame.init()

class VisualState(ObservableState):
    def __init__(self):
        super(VisualState,self).__init__()
        pygame.display.set_caption('Rampyge')
        self.screenWidth = 482
        self.screenHeight = 721
        self.font = pygame.font.SysFont('Arial', 18)
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        self.img_path = 'images/tank.gif'
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((20, 150, 0))   
        
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
        pygame.draw.line(self.scrBuff,BLACK,self.pos,self.pos, 4)
        pygame.draw.circle(self.scrBuff,RED,(int(self.targetPos[0]), int(self.targetPos[1])), 4)
        rotImg.get_rect().center = loc
        
        surface.blit(rotImg, (self.pos[0] - rotImg.get_rect().width/2.0,
                              self.pos[1] - rotImg.get_rect().height/2.0))
        
        pygame.display.update()      # update the screen
        if self.isCollision == False:
            pygame.draw.aalines(self.screen, BLACK, True, ((self.scanCone[0]), self.scanCone[1], self.scanCone[2]))
        else:
            pygame.draw.aalines(self.screen, RED, True, ((self.scanCone[0]), self.scanCone[1], self.scanCone[2]))
        #pygame.gfxdraw.filled_polygon(self.screen,  ((self.scanCone[0]), self.scanCone[1], self.scanCone[2]), BLACK)
       # pygame.gfxdraw.filled_polygon(self.screen, self.scanCone[0,1,2], BLACK)
       # print self.scanCone
        
        
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
        #pygame.draw.polygon(self.background, GREEN, [
        #    [120, 720],[120,480],
        #    [0,480],[0,0],
        #    [480,0],[480,480],
        #    [360,480],[360,720]])    
        pygame.draw.circle(self.scrBuff,WHITE,(self.waypoint[0], self.screenHeight - self.waypoint[1]), 4,)
        pygame.draw.circle(self.scrBuff,BLACK,(self.waypoint[0], self.screenHeight - self.waypoint[1]), 4, 2)
                    
        for wall in self.wallList:
            self.wall = (wall[0], self.screenHeight - wall[1], wall[2], self.screenHeight - wall[3])
            pygame.draw.line(self.scrBuff, BLACK, (self.wall[0], self.wall[1]), (self.wall[2], self.wall[3]), 4 )
            
        for pole in self.poleList:
            self.pole = (pole[0], self.screenHeight - pole[1])
            pygame.draw.circle(self.scrBuff,BLUE,self.pole, 10,)
            pygame.draw.circle(self.scrBuff,BLACK,self.pole, 10, 2)
            
    def drawInfoPanel(self,surface):
        self.screen.blit(self.font.render(("Information"), True, BLACK), (15,490))
        
        self.screen.blit(self.font.render(("Target: ({0},{1})".format(int(self.targetPos[0]), self.screenHeight - int(self.targetPos[1]))), True, BLACK), (3,515))
        self.screen.blit(self.font.render(("(x , y): ({0},{1})".format(int(self.pos[0]), self.screenHeight - int(self.pos[1]))), True, BLACK), (3,535))
        self.screen.blit(self.font.render(("Angle (deg): {0}".format(int(self.angle))), True, BLACK), (3,555))
        self.screen.blit(self.font.render(("Angle (rad): {0:.2f}".format(math.radians(self.angle))), True, BLACK), (3,575))
        
        self.screen.blit(self.font.render(("Max: {0:.3f}".format(self.max)), True, BLACK), (3,595))
        self.screen.blit(self.font.render(("Min: {0:.3f}".format(self.min)), True, BLACK), (3,615))
        self.screen.blit(self.font.render(("Average: {0:.3f}".format(self.average)), True, BLACK), (3,635))
        self.screen.blit(self.font.render(("Length: {0}".format(self.length)), True, BLACK), (3,655))
        self.screen.blit(self.font.render(("Variance: {0:.3f}".format(self.variance)), True, BLACK), (3,675))
        
        pygame.display.update()      # update the screen
        
def visualControlUpdate(state,batchdata):
    
    state.removeLastWP = False
    for event in pygame.event.get():          # handle every event since the last frame.
        if event.type == pygame.QUIT:
            pygame.quit()       # quit the screen
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            pos = (event.pos[0], state.screenHeight - event.pos[1])
            print "You pressed at locaton: ", pos
            state.waypoint = pos
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            print "Right click"
            state.removeLastWP = True
            
   # print state.removeLastWP
    state.screen.fill(WHITE) # fill the screen with white
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
    if len(batchdata) == 0: return

def visualToRouteTranslator(sourceState, destState, destQueue):
    if sourceState.waypoint != (0,0) and sourceState.waypoint != sourceState.prevWaypoint:
        sourceState.prevWaypoint = sourceState.waypoint
        message = {'messageType':'waypoint',
                   'newWaypoint'    :sourceState.waypoint,
                   'removeWaypoint' :sourceState.removeLastWP}
        destQueue.put(message)


        
