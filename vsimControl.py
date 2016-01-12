import time
import math
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class VsimState(ObservableState):
    def __init__(self, fricEffectPerSec, lrBias, speedMax):
        super(VsimState,self).__init__()        
        self.speedL = 0.0 # mm/sec
        self.speedR = 0.0 # mm/sec
        self.rcTurn = 0.0
        self.rcFwd = 0.0
        self.timeDelta = 0.0
        self._fricEffectPerSec = fricEffectPerSec #0.95 #deceleration effect
        self._lrBias = lrBias #1.0
        self._speedMax = speedMax #600.0 # to mm/sec
        self._leftSpeedMultiplier = self._speedMax * self._lrBias
        self._rightSpeedMultiplier = self._speedMax / self._lrBias
        self.timeStamp = time.time()


        
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

    demandL = state._leftSpeedMultiplier * (state.rcFwd + state.rcTurn) / 2.0
    demandR = state._rightSpeedMultiplier * (state.rcFwd - state.rcTurn) / 2.0 # demand 2.0 == max turn + max fwd
    
    state.speedL = speedUpdate(state.speedL,demandL,state.timeDelta,state._fricEffectPerSec)
    state.speedR = speedUpdate(state.speedR,demandR,state.timeDelta,state._fricEffectPerSec)

    #print "speedl", state.speedL
    #print "speedr", state.speedR

def speedUpdate( current, demanded, tDelta, fricPerSec):
    fricNow = fricPerSec * current * tDelta 
    fricTerminal = fricPerSec * demanded * tDelta
    return current - fricNow + fricTerminal
    
def vsimToOdoTranslator( sourceState, destState, destQueue ):
    deltaL = round(sourceState.speedL * sourceState.timeDelta / destState._mmPerPulse ,0)
    deltaR = round(sourceState.speedR * sourceState.timeDelta / destState._mmPerPulse ,0)
    rollover = destState._rolloverRange
    
    left = (destState.totalPulseL + deltaL) % rollover
    right = (destState.totalPulseR + deltaR) % rollover
    message = {'messageType':'sense',
               'pulseL':left,
               'pulseR':right  }
    destQueue.put(message)
    
