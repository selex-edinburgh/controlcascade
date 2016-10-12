import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator
from lib.navigation import *

class ScanSimState(ObservableState):
    def __init__(self, sensorID, sensorPosOffset, sensorHdgOffset, scanAngle, scanRange, turnSpeed):
        super(ScanSimState,self).__init__()
        self.sensorID = sensorID
        self.sensorPosOffset = sensorPosOffset
        self.sensorHdgOffset = sensorHdgOffset
        self.scanAngle = scanAngle
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

    # determine the points of the scanning cone
    a = sensorToWorld(state.robotPos,state.robotAngle, state.sensorPosOffset, state.sensorHdgOffset,(0,0)) 
    b = sensorToWorld(state.robotPos,state.robotAngle, state.sensorPosOffset, state.sensorHdgOffset,(state.scanRange,-state.scanAngle/2))
    c = sensorToWorld(state.robotPos,state.robotAngle, state.sensorPosOffset, state.sensorHdgOffset,(state.scanRange,state.scanAngle/2))
    
    state.scanCone = [a,b,c]        # three points of scan cone
    
    anyCollisions = False 
    
    for p in state.poleList:        # check for collision against each pole
       if collisionWarn(a,b,c,p):
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
