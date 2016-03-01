# -*- coding: utf-8 -*-
import time
import math
import threading
try:
    import serial
except:
    print "Serial not connected.."
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class RcChanState(ObservableState):
    def __init__(self, limitChange, speedLimit):
        super(RcChanState,self).__init__()
        self.currentTurn = 127
        self.currentFwd = 127
        self.demandTurn = 127
        self.demandFwd = 127
        self._limitChange = limitChange #80
        self.timeStamp    = time.time()
        self.minClip = 127 - speedLimit
        self.maxClip = 127 + speedLimit
        
        self.timeStampFlow["control"] = time.time()

        try:
            self.ser= serial.Serial(                     #Set up Serial Interface    
            port="/dev/ttyAMA0",                #UART using Tx pin 8, Rx pin 10, Gnd pin 6   
            baudrate=9600,                      #bits/sec      
            bytesize=8, parity='N', stopbits=1, #8-N-1  protocol     
            timeout=1                           #1 sec       
            )
        except:
            print "Serial not connected..."

    def clip(self, x):
        #if x < 0 or x >255: print "clip"
        return min(self.maxClip,max(self.minClip,x))
   
def simMotor(state, batchdata):
    rcChanControlUpdate(state, batchdata, False)

def realMotor(state, batchdata):
    rcChanControlUpdate(state, batchdata, True)
        
        
def rcChanControlUpdate(state,batchdata,motorOutput):
    
    for item in batchdata:      # process items in batch data
    
        if 'timeStamp' in item:
            state.timeStampFlow[item['messageType']] = item['timeStamp']

        if item['messageType'] == 'control':
            state.demandTurn = state.clip(-item['demandTurn'] * 127 + 127)## expects anti clockwise
            state.demandFwd =  state.clip(item['demandFwd'] * 127 + 127) ####inserted minus
            
        elif item['messageType'] == 'sense':
            pass
        
    state.currentTurn = limitedChange(state.currentTurn, state.demandTurn , state._limitChange )
    state.currentFwd = limitedChange(state.currentFwd, state.demandFwd , state._limitChange )
    
    if motorOutput:
        state.ser.write(chr((int(state.currentFwd))))  #Output to Motor Drive Board     
        state.ser.write(chr((int(state.currentTurn))) )      #Output to Motor Drive Board      

    
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

def rcChanToStatsTranslator(sourceState, destState, destQueue):
    timeStamp = time.time()
    destQueue.put({'messageType':'motor',
                    'time': timeStamp,
                    'rcTurn' : sourceState.currentTurn,
                    'rcFwd' : sourceState.currentFwd})