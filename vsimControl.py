import time
import math
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

vsimState = ObservableState()
vsimState.speedL = 0.0 # mm/sec
vsimState.speedR = 0.0 # mm/sec
vsimState.rcTurn = 0.0
vsimState.rcFwd = 0.0
vsimState.timeStamp = time.time()

def vsimControlUpdate(state,batchdata):
    #process items in batchdata
    prevRcTurn = state.rcTurn
    prevRcFwd = state.rcFwd

    for item in batchdata:
        if item['messageType'] == 'control':
            state.rcTurn = item['rcTurn']
            state.rcFwd = item['rcFwd']
        elif item['messageType'] == 'sense':
            print "Sense messages not implemented for vsimControl"
    
    prevTimeStamp = vsimState.timeStamp
    state.timeStamp = time.time()
    timeDelta = state.timeStamp - prevTimeStamp
    
    accelerateL = 
    accelerateR = 
