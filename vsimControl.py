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
vsimState.timeDelta = 0.0
vsimState._fricEffectPerSec = 0.95 #deceleration effect
vsimState._lrBias = 1.0
vsimState._speedMax = 600.0 # to mm/sec
vsimState._leftSpeedMultiplier = vsimState._speedMax * vsimState._lrBias
vsimState._rightSpeedMultiplier = vsimState._speedMax / vsimState._lrBias

def vsimControlUpdate(state,batchdata):
    #process items in batchdata
    prevRcTurn = state.rcTurn
    prevRcFwd = state.rcFwd
    #print "Batch in vsim len = ",len(batchdata)
    for item in batchdata:
        if item['messageType'] == 'control':
            #print item
            state.rcTurn = item['rcTurn'] 
            state.rcFwd = item['rcFwd']
        elif item['messageType'] == 'sense':
            print "Sense messages not implemented for vsimControl"
    
    prevTimeStamp = state.timeStamp
    state.timeStamp = time.time()
    state.timeDelta = state.timeStamp - prevTimeStamp

    demandL = state._leftSpeedMultiplier * (state.rcFwd - state.rcTurn) / 2.0 # demand 2.0 == max turn + max fwd
    demandR = state._rightSpeedMultiplier * (state.rcFwd + state.rcTurn) / 2.0
    
    state.speedL = speedUpdate(state.speedL,demandL,state.timeDelta,state._fricEffectPerSec)
    state.speedR = speedUpdate(state.speedR,demandR,state.timeDelta,state._fricEffectPerSec)

    #print "speedl", state.speedL
    #print "speedr", state.speedR

def speedUpdate( current, demanded, tDelta, fricPerSec):
    fricNow = fricPerSec * current * tDelta 
    fricTerminal = fricPerSec * demanded * tDelta
    return current - fricNow + fricTerminal
    
def vsimToOdoTranslator( sourceState, destState, destQueue ):
    message = {'messageType':'sense',
               'pulseL':round(sourceState.speedL * sourceState.timeDelta / destState._mmPerPulse ,0),
               'pulseR':round(sourceState.speedR * sourceState.timeDelta / destState._mmPerPulse ,0)}
    destQueue.put(message)
    
