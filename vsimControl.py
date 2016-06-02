import time
import math
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class VsimState(ObservableState):
    def __init__(self, fricEffectPerSec, lrBias, speedMax):
        super(VsimState,self).__init__()        
        self.speedL = 0.0       #  mm/sec
        self.speedR = 0.0       #  mm/sec
        self.rcTurn = 0.0
        self.rcFwd = 0.0
        self.timeDelta = 0.0
        self._fricEffectPerSec = fricEffectPerSec       # 0.95 #deceleration effect
        self._lrBias = lrBias        # 1.0
        self._speedMax = speedMax       # 600.0 # to mm/sec
        self._leftSpeedMultiplier = self._speedMax * self._lrBias
        self._rightSpeedMultiplier = self._speedMax / self._lrBias
        self.timeStampFlow["sense"] = time.time()
        self.timeStamp= time.time()
     
def vsimControlUpdate(state,batchdata):
    prevRcTurn = state.rcTurn
    prevRcFwd = state.rcFwd
 
    for item in batchdata:      # process items in batchdata
        if 'timeStamp' in item:
            state.timeStampFlow[item['messageType']] = item['timeStamp']
            
        if item['messageType'] == 'control':
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
    
    destQueue.put({'messageType':'sense',
               'pulseL':left,
               'pulseR':right,
               'timeStamp':sourceState.timeStampFlow["sense"]})


    
