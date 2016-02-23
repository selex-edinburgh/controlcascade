import math
import threading
import time
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class SensorState(ObservableState):
    def __init__(self, scanDist, scanRange):
        super(SensorState,self).__init__()
        self.scanDist = scanDist
        self.scanRange = scanRange
        self.poleList = []
        self.wallList = []
        self.timeStamp    = time.time()
        
def sensorControlUpdate(state,batchdata):
    for item in batchdata:
        if item['messageType'] == 'control':
            pass
            
        elif item['messageType'] == 'sense':
            state.poleList = item['sensedPole']
            state.wallList = item['sensedWall']
    state.timeStamp = time.time()
    
    

def sensorToTrackTranslator(sourceState, destState, destQueue):

    poleList = sourceState.poleList
    robotPos = destState.currentPos
    for pole in poleList:
        diffA = pole[0] - (robotPos[0]/10)
        diffB = pole[1] - (robotPos[1]/10)
        
      
        if (diffA < 100) & (diffB < 100):        # If chariot within range of an obstacle     
            message = {'messageType':'obstacle','obsPosition': pole}
            destQueue.put(message)
