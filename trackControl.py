# -*- coding: utf-8 -*-
import time
import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class TrackState(ObservableState):
    def __init__(self, trackWidth, movementBudget):
        super(TrackState,self).__init__()    
        self.sensedMove = 0
        self.timeout = time.time() + 4       # 4 seconds
        self.demandFwd = 0
        self.demandTurn = 0
        self.noLegSet = True
        self.legCoeff  = (0.0,0.0,0.0)        
        self.legGoal = (0.0,0.0)     
        self.legOrigin = (0.0,0.0)
        self.currentAngle = 0
        self.currentPos = (2390.0,4630.0,0)           
        self.demandAngle = 0
        self.demandPos = (0.0,0,0)            
        self._trackWidth = trackWidth       # 310.0 mm between wheels
        self._movementBudget = movementBudget       # 500.0 mm
        self.timeStamp = time.time()
        self.pole = (1200,0)
        self.timeStampFlow["control"] = time.time()
        self.timeStampFlow["sense"] = time.time()
        self.isCollision = False
        self.nearWaypoint = False  
    
def trackControlUpdate(state,batchdata):   

    for item in batchdata:
        if item['messageType'] == 'sense':
            state.sensedMove = item['sensedMove']
            state.sensedAngle = item['sensedAngle']
        
    
    
    if time.time() < state.timeout:
        state.demandFwd = 0.2
        state.demandTurn  = 0
    else:
        state.demandFwd = 0
        state.demandTurn = 0

            
            
def trackToRcChanTranslator( sourceState, destState, destQueue ):
   
    
    message = {'messageType':'control','demandTurn': sourceState.demandTurn,
                                       'demandFwd' : sourceState.demandFwd
                                       }
    destQueue.put(message)

