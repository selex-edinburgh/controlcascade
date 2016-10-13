'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
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

