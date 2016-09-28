import math
import threading
import time
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class ScanSimState(ObservableState):
    def __init__(self, sensorID, pointAOffset, pointB, pointC, scanAngle, scanRange, turnSpeed):
        super(ScanSimState,self).__init__()
        self.sensorID = sensorID
        self.pointAOffset = pointAOffset
        self.pointB = pointB
        self.pointC = pointC
        self.scanAngle = scanAngle
        self.scanRange = scanRange
        self.turnSpeed = turnSpeed
        self.robotPos = (1200.0,0.0)
        self.robotAngle = 0.0
        self.poleList = [(0.0),(0.0)]
        self.scanCone = []
        self.isCollision = False
        self.angleIncrementor = 0
        self.increment = 5
        self.sensorID = sensorID
        
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
    
    state.angleIncrementor += state.increment # used to change pointB and pointC so that scanCone moves left to right
    if state.angleIncrementor >= state.scanAngle or state.angleIncrementor <= -state.scanAngle: # test with 135 and 45
        state.increment *= -1
        
    a = ((state.robotPos[0] / 10), (720 -( state.robotPos[1]) / 10) + state.pointAOffset)# determine the points of the scanning cone
    
    b = ((a[0] + state.scanRange * math.cos(math.radians(state.robotAngle- (state.pointB+state.angleIncrementor)))), \
        (a[1] + state.scanRange * math.sin(math.radians(state.robotAngle- (state.pointB+state.angleIncrementor)))))
    
    c =   ((a[0] + state.scanRange * math.cos(math.radians(state.robotAngle  - (state.pointC+state.angleIncrementor)))), \
        (a[1] + state.scanRange * math.sin((math.radians(state.robotAngle - (state.pointC+state.angleIncrementor))))))
    
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
                'sensorID':sourceState.sensorID,
                'scanCone': sourceState.scanCone,
                'collision': sourceState.isCollision}
    destQueue.put(message)

def scanSimToVisualTranslator(sourceState, destState, destQueue):
    message = {'messageType':'scan',
                'sensorID':sourceState.sensorID,
                'scanCone': sourceState.scanCone,
                'collision': sourceState.isCollision}
    destQueue.put(message)
