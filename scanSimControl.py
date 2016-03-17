import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class ScanSimState(ObservableState):
    def __init__(self, scanRange, turnSpeed):
        super(ScanSimState,self).__init__()
        self.scanRange = scanRange
        self.turnSpeed = turnSpeed
        self.robotPos = (1200.0,0.0)
        self.robotAngle = 0.0
        self.poleList = [(0.0),(0.0)]
        self.scanCone = []
        self.isCollision = False
        
def scanSimControlUpdate(state, batchdata):
    for item in batchdata:
        if item['messageType'] == 'control':
            pass
            
        elif item['messageType'] == 'sense':
            state.robotPos = (item['sensedPos'])
            state.robotAngle = (item['sensedAngle'])
        elif item['messageType'] == 'obstacle':
            state.poleList = (item['poleList'])
            
    if len(batchdata) == 0: return
        
    a = ((state.robotPos[0] / 10), (720 -( state.robotPos[1]) / 10))        # determine the points of the scanning cone
    
    b = ((a[0] + state.scanRange * math.cos(math.radians(state.robotAngle- 135))), \
        (a[1] + state.scanRange * math.sin(math.radians(state.robotAngle- 135))))
    
    c =   ((a[0] + state.scanRange * math.cos(math.radians(state.robotAngle  -45))), \
        (a[1] + state.scanRange * math.sin((math.radians(state.robotAngle - 45)))))
    
    state.scanCone = [a,b,c]        # three points of scan cone
    
    newA = (a[0], (720 - a[1]))     # adjustment for screen height 
    newB = (b[0], (720 - b[1]))
    newC = (c[0], (720 - c[1]))
    
    anyCollisions = False 
    
    for p in state.poleList:        # check for collision against each pole
       if collisionWarn(newA,newB,newC,p):
           anyCollisions = True
           break 
    state.isCollision = anyCollisions
    
def collisionWarn(p0,p1,p2,p):      # helper function that returns if pole falls within scan range
    A = 0.5 * (-p1[1] * p2[0] + p0[1] * (-p1[0] + p2[0]) + p0[0] * (p1[1] - p2[1]) + p1[0] * p2[1])
    sign = 1
    if A < 0:
        sign = -1
    s = (p0[1] * p2[0] - p0[0] * p2[1] + (p2[1] - p0[1]) * p[0] + (p0[0] - p2[0]) * p[1]) * sign
    t = (p0[0] * p1[1] - p0[1] * p1[0] + (p0[1] - p1[1]) * p[0] + (p1[0] - p0[0]) * p[1]) * sign
    
    return s > 0 and t > 0 and (s + t) < 2 * A * sign;

def scanSimToSensorTranslator( sourceState, destState, destQueue):
    message = {'messageType':'sense',
                'scanCone': sourceState.scanCone,
                'collision': sourceState.isCollision}
    destQueue.put(message)

def scanSimToVisualTranslator(sourceState, destState, destQueue):
    message = {'messageType':'scan',
                'scanCone': sourceState.scanCone,
                'collision': sourceState.isCollision}
    destQueue.put(message)