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
            
    if len(batchdata) == 0: return      # return if batchdata is empty
    pointA = ((state.robotPos[0] / 10), (720 -( state.robotPos[1]) / 10))        # determine the points of the scanning cone
    
    pointB = ((pointA[0] + state.scanRange * math.cos(math.radians(state.robotAngle- 135))), \
        (pointA[1] + state.scanRange * math.sin(math.radians(state.robotAngle- 135))))
    
    pointC =   ((pointA[0] + state.scanRange * math.cos(math.radians(state.robotAngle  -45))), \
        (pointA[1] + state.scanRange * math.sin((math.radians(state.robotAngle - 45)))))
    
    state.scanCone = [pointA,pointB,pointC]        # three points of scan cone
    
    newA = (pointA[0], (720 - pointA[1]))     # adjustment for screen height 
    newB = (pointB[0], (720 - pointB[1]))
    newC = (pointC[0], (720 - pointC[1]))
    
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
    destQueue.put({'messageType':'sense',
                'scanCone': sourceState.scanCone,
                'collision': sourceState.isCollision})

def scanSimToVisualTranslator(sourceState, destState, destQueue):
    destQueue.put({'messageType':'scan',
                'scanCone': sourceState.scanCone,
                'collision': sourceState.isCollision})
