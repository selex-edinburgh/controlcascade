# -*- coding: utf-8 -*-
import time
import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class OdoState(ObservableState):
    def __init__(self,mmPerPulse=0.1,rolloverRange=4096,rolloverCountL=0,rolloverCountR=0,initTheta=math.pi/2.0):
        super(OdoState,self).__init__()
        self.totalPulseL = 0
        self.totalPulseR = 0
        self.prevPulseL = 0
        self.prevPulseR = 0
        self.prevDistTravel = 0
        self.distTravel = 0
        self._initTheta = initTheta
        self._mmPerPulse = mmPerPulse #0.1
        self._rolloverRange = rolloverRange #4096
        self._rolloverCountL = rolloverCountL #0
        self._rolloverCountR = rolloverCountR #0
        self.timeStamp = time.time()
        
#odoState = OdoState(0.1,4096,0,0,math.pi/2) #OdoState(mmPerPulse,rolloverRange,rolloverCountL,rolloverCountR)

def odoControlUpdate(state,batchdata):
    state.prevPulseL = state.totalPulseL
    state.prevPulseR = state.totalPulseR
    #process items in batchdata
    for item in batchdata:
        if item['messageType'] == 'control':
            pass
        elif item['messageType'] == 'sense':
            leftReading = item['pulseL']
            rightReading = item['pulseR']
    
    #can get state.totalPulseL, state.totalPulseR from i2c here
    readI2C = False        
    if not(readI2C) and len(batchdata)==0 : return
    #account for any rollover here
    state.totalPulseL = leftReading + state._rolloverCountL * state._rolloverRange
    state.totalPulseR = rightReading + state._rolloverCountR * state._rolloverRange
    #print "#### test rollover r", state.totalPulseR, state.prevPulseR

    if ( abs(state.totalPulseL - state.prevPulseL  ) > state._rolloverRange / 2 ) :
        sign = math.copysign(1, state.totalPulseL - state.prevPulseL  )
        state._rolloverCountL -= sign
        state.totalPulseL = leftReading + state._rolloverCountL * state._rolloverRange
        print "#################### rollover l", state.totalPulseL, state.prevPulseL
    if ( abs(state.totalPulseR - state.prevPulseR  ) > state._rolloverRange / 2 ) :
        sign = math.copysign(1, state.totalPulseR - state.prevPulseR  )
        state._rolloverCountR -= sign
        state.totalPulseR = rightReading + state._rolloverCountR * state._rolloverRange
        print "#################### rollover r", state.totalPulseR, state.prevPulseR

    state.prevDistTravel = state.distTravel
    state.distTravel +=  (( state.totalPulseL - state.prevPulseL ) + (state.totalPulseR -  state.prevPulseR )) / 2.0 * state._mmPerPulse
    
    
def odoToTrackTranslator( sourceState, destState, destQueue ):
    lrDifferenceMm = (sourceState.totalPulseR - sourceState.totalPulseL) * sourceState._mmPerPulse 
    #print "odo dist " , sourceState.distTravel - sourceState.prevDistTravel           
    theta = lrDifferenceMm / destState._trackWidth + sourceState._initTheta# + math.pi / 2.0# circumferential move divided by radius to give angle in radians
                # TODO work around fudge to get robot pointing north at start (pi/2)
    destQueue.put({'messageType':'sense',
                   'sensedMove' :sourceState.distTravel - sourceState.prevDistTravel,
                   'sensedTheta':theta}) 


      
    
