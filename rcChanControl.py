'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
# -*- coding: utf-8 -*-
import time
import math
import os
import threading
try:
    import serial
except:
    print "Serial not connected.."
from plumbing.observablestate import ObservableState
from plumbing.arcnode import ArcNodeObserverTranslator

'''
    Uncomment this section and motorCommand file open part further down to
    get back motor date to put in Graphs
'''
##try:        # delete log file
##    os.rename('motorCommands.txt','log/%s.old' % time.time())
##    os.remove('motorCommands.txt')
##except OSError:
##    print "os fail"

class RcChanState(ObservableState):
    def __init__(self, lrChange, fwdbkChange, speedScalingFwdBk, speedScalingLR, turnOffset = 0, turnBiasLOverR = 1.0):
        super(RcChanState,self).__init__()
        self._nullFwd = 127
        self._nullTurn = 127 + turnOffset
        self._turnBiasLOverR = turnBiasLOverR
        self._maxDemand = 127
        self.currentTurn = self._nullTurn
        self.currentFwd = self._nullFwd
        self.demandTurn = self._nullTurn
        self.demandFwd = self._nullFwd
        self.speedScalingFwdBk = speedScalingFwdBk
        self.speedScalingLR = speedScalingLR
        self._lrChange = lrChange * speedScalingLR
        self._fwdbkChange = fwdbkChange * speedScalingFwdBk
        self.timeStamp    = time.time()

        self.timeStampFlow["control"] = time.time()
        try:
            self.ser= serial.Serial(            #Set up Serial Interface
            port="/dev/ttyS0",                #UART using Tx pin 8, Rx pin 10, Gnd pin 6
            baudrate=38400,                      #bits/sec
            bytesize=8, parity='N', stopbits=1, #8-N-1  protocol
            timeout=1                           #1 sec
            )
        except:
            print "Serial not connected..."

    def clip(self, x):
        return min(254,max(1,x))

def simMotor(state, batchdata):
    rcChanControlUpdate(state, batchdata, False)

def realMotor(state, batchdata):
    rcChanControlUpdate(state, batchdata, True)

def rcChanControlUpdate(state,batchdata, motorOutput):
    for item in batchdata:      # process items in batchdata

        if 'timeStamp' in item:
            state.timeStampFlow[item['messageType']] = item['timeStamp']
            pass

        if item['messageType'] == 'control':
                state.demandTurn = state.clip(item['demandTurn'] * state.speedScalingLR * state._maxDemand + state._nullTurn)   ## expects anti clockwise
                state.demandFwd  = state.clip(item['demandFwd'] * state.speedScalingFwdBk * state._maxDemand + state._nullFwd)   ## inserted minus
                state.demandTurn = state.demandTurn * state._turnBiasLOverR if state.demandTurn > 0.0 else state.demandTurn / state._turnBiasLOverR
        elif item['messageType'] == 'sense':
            pass

    if not batchdata:       # if no messages (loops stopped) set the speed to stationary
        state.demandFwd = state._nullFwd
        state.demandTurn = state._nullTurn


    state.currentTurn = min(255,max(0, limitedChange(state.currentTurn, state.demandTurn , state._lrChange )))
    state.currentFwd = min(255,max(0, limitedChange(state.currentFwd, state.demandFwd , state._fwdbkChange )))

##    f = open('motorCommands.txt', 'a')
##
##    print >> f, time.time(), ",", int(state.currentFwd), ",", int(state.currentTurn)
##
##    f.close()
    
    if motorOutput:
        state.ser.write(chr((int(state.currentFwd))))  #Output to Motor Drive Board
        state.ser.write(chr((int(state.currentTurn))) )      #Output to Motor Drive Board
        
##    if time.time() - int(time.time()) < 0.05: print state.currentFwd, state.currentTurn#, state.demandFwd, state.demandTurn
        
def limitedChange(startX, endX, magnitudeLimit):
    diff = endX - startX
    if diff == 0: return startX
    diffSign = math.copysign(1,diff)
    change = diffSign * ( min(abs(diff),magnitudeLimit) )
    return startX + change

def rcChanToVsimTranslator( sourceState, destState, destQueue ):
    destQueue.put({'messageType':'control',
                   'rcTurn' :-(sourceState.currentTurn/sourceState._maxDemand - 1.0),
                   'rcFwd'  :sourceState.currentFwd/sourceState._maxDemand - 1.0 ,
                   'timeStamp' : sourceState.timeStampFlow})
