import math
import threading
import time
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class SensorState(ObservableState):
    def __init__(self, scanDist, scanRange):
        super(SensorState,self).__init__()
        self.scanRange = 100.0
        self.turnSpeed = 0.0
        self.scanCone = [(0.0)]
        self.timeStamp    = time.time()
        self.isCollision = False
        
def sensorControlUpdate(state,batchdata):
    for item in batchdata:
        if item['messageType'] == 'control':
            pass
            
        elif item['messageType'] == 'sense':
            state.scanCone = item['scanCone']
            state.isCollision = item['collision']
            
def sensorToTrackTranslator(sourceState, destState, destQueue):
    message = {'messageType':'obstacle',
            'collision': sourceState.isCollision}
    destQueue.put(message)
