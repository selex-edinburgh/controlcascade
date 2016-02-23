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
        self.scanCone = ()
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
    
    
    #print state.robotPos, state.robotAngle
    
    print state.robotAngle
    a = ((state.robotPos[0] / 10), (720 -( state.robotPos[1]) / 10))
    
    b = ((a[0] + state.scanRange * math.cos(math.radians(state.robotAngle- 110))), (a[1] + state.scanRange * math.sin(math.radians(state.robotAngle- 110))))
    
    c =   ((a[0] + state.scanRange * math.cos(math.radians(state.robotAngle - 70))),(a[1] + state.scanRange * math.sin((math.radians(state.robotAngle - 70)))))
    
    state.scanCone = (a,b,c)
    
    
def scanSimToSensorTranslator( sourceState, destState, destQueue):
    message = {'messageType':'sense','sensedPos':sourceState.polePos}
    destQueue.put(message)

def scanSimToVisualTranslator(sourceState, destState, destQueue):
    message = {'messageType':'scan',
                'scanCone': sourceState.scanCone}
    destQueue.put(message)