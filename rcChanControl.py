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
from plumbing.controlloop import ControlObserverTranslator

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
    def __init__(self, lrChange, fwdbkChange, speedScaling):
        super(RcChanState,self).__init__()
        self.currentTurn = 127
        self.currentFwd = 127
        self.demandTurn = 127
        self.demandFwd = 127
        self.speedScaling = speedScaling
        self._lrChange = lrChange * speedScaling
        self._fwdbkChange = fwdbkChange * speedScaling
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
            if motorOutput:
                state.demandTurn = state.clip(item['demandTurn'] * state.speedScaling * 127 + 127)   ## expects anti clockwise
                state.demandFwd  = state.clip(-item['demandFwd'] * state.speedScaling * 127 + 127)   ## inserted minus
            else:
                state.demandTurn = state.clip(-item['demandTurn'] * state.speedScaling * 127 + 127)  ## expects anti clockwise
                state.demandFwd  = state.clip(item['demandFwd'] * state.speedScaling * 127 + 127)    ## inserted minus

        elif item['messageType'] == 'sense':
            pass

    if not batchdata:       # if no messages (loops stopped) set the speed to stationary
        state.demandFwd = 127
        state.demandTurn = 127


    state.currentTurn = limitedChange(state.currentTurn, state.demandTurn , state._lrChange )
    state.currentFwd = limitedChange(state.currentFwd, state.demandFwd , state._fwdbkChange )

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
                   'rcTurn' :-(sourceState.currentTurn/127.0 - 1.0),
                   'rcFwd'  :sourceState.currentFwd/127.0 - 1.0 ,
                   'timeStamp' : sourceState.timeStampFlow})
