# -*- coding: utf-8 -*-
import time
import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class TrackState(ObeservableState):
    def __init__(self, trackWidth, movementBudget): 
        self.sensedMove = 0
        state.timeout = time.time() + 4       # 4 seconds
        state.demandFwd = 0
        state.demandTurn = 0
    
def trackControlUpdate(state,batchdata):   

    for item in batchdata:
        if item['messageType'] == 'sense':
            state.sensedMove = item['sensedMove']
            state.sensedAngle = item['sensedAngle']
        
    
    
    if time.time() > state.timeout:
        state.demandFwd = 0.2
        state.demandTurn  = 0

            
            
def trackToRcChanTranslator( sourceState, destState, destQueue ):
   
    
    message = {'messageType':'control','demandTurn': state.demandTurn,
                                       'demandFwd' : state.demandFwd
                                       }
    destQueue.put(message)

