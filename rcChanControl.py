# -*- coding: utf-8 -*-
import time
import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class RcChanState(ObservableState):
    def __init__(self, limitChange):
        super(RcChanState,self).__init__()
        self.currentTurn = 127
        self.currentFwd = 127
        self.demandTurn = 127
        self.demandFwd = 127
        self._limitChange = limitChange #80
        self.timeStamp    = time.time()


        
def rcChanControlUpdate(state,batchdata):
    #process items in batchdata
    for item in batchdata:
        if item['messageType'] == 'control':
            state.demandTurn = clip(-item['demandTurn'] * 127 + 127)
            state.demandFwd =  clip(item['demandFwd'] * 127 + 127)
        elif item['messageType'] == 'sense':
            pass
        
    state.currentTurn = limitedChange(state.currentTurn, state.demandTurn , state._limitChange )
    state.currentFwd = limitedChange(state.currentFwd, state.demandFwd , state._limitChange )
    #print "rcChan ", state.currentTurn, state.currentFwd
    
def limitedChange(startX, endX, magnitudeLimit):
    diff = endX - startX
    if diff == 0: return startX
    diffSign = math.copysign(1,diff)
    change = diffSign * ( min(abs(diff),magnitudeLimit) )
    return startX + change
    
def clip(x):
    #if x < 0 or x >255: print "clip"
    return min(255,max(0,x))

def rcChanToVsimTranslator( sourceState, destState, destQueue ):
    destQueue.put({'messageType':'control',
                   'rcTurn' :-(sourceState.currentTurn/127.0 - 1.0),
                   'rcFwd'  :sourceState.currentFwd/127.0 - 1.0 }) 

      
    
