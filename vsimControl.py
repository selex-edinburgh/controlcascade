'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import time
import math
from plumbing.observablestate import ObservableState
from plumbing.arcnode import ArcNodeObserverTranslator

class VsimState(ObservableState):
    def __init__(self, lrBias, speedMax):
        super(VsimState,self).__init__()        
        self.speedL = 0.0       #  mm/sec
        self.speedR = 0.0       #  mm/sec
        self.rcTurn = 0.0
        self.rcFwd = 0.0
        self.timeDelta = 0.0
        self._lrBias = lrBias        
        self._speedMax = speedMax   # to mm/sec
        self._leftSpeedMultiplier = self._speedMax * self._lrBias
        self._rightSpeedMultiplier = self._speedMax / self._lrBias
        self.timeStampFlow["sense"] = time.time()
        self.timeStamp= time.time()
        self.vSimLog = open('vSimLog.csv', 'w')
        #print >> self.vSimLog, 'vSim', ', ', 'rcTurn', ', ', 'rcFwd', ', ', 'speedL', ', ', 'speedR', ', '
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

    state.speedL = state._leftSpeedMultiplier * (state.rcFwd + state.rcTurn) / 2.0
    state.speedR = state._rightSpeedMultiplier * (state.rcFwd - state.rcTurn) / 2.0 # demand 2.0 == max turn + max fwd

    #print >> state.vSimLog, 'vSim', ', ', state.rcTurn, ', ', state.rcFwd, ', ', state.speedL, ', ', state.speedR, ', '

def vsimToOdoTranslator( sourceState, destState, destQueue ):
    deltaL = round(sourceState.speedL * sourceState.timeDelta / destState._mmPerPulseLt ,0)
    deltaR = round(sourceState.speedR * sourceState.timeDelta / destState._mmPerPulseRt ,0)
    rollover = destState._rolloverRange
    
    left = (destState.totalPulseL + deltaL) % rollover
    right = (destState.totalPulseR + deltaR) % rollover
    message = {'messageType':'sense',
               'pulseL':left,
               'pulseR':right,
               'timeStamp':sourceState.timeStampFlow["sense"]}
    destQueue.put(message)

    
