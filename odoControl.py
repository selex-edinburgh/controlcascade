# -*- coding: utf-8 -*-
import time
import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

odoState = ObservableState()

odoState.timeStamp    = time.time()
odoState.totalPulseL = 0
odoState.totalPulseR = 0
odoState.prevPulseL = 0
odoState.prevPulseR = 0
odoState.prevDistTravel = 0
odoState.distTravel = 0
odoState._mmPerPulse = 0.1
odoState._rolloverRange = 4096
odoState._rolloverCountL = 0
odoState._rolloverCountR = 0

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
    theta = lrDifferenceMm / destState._trackWidth + math.pi / 2.0# circumferential move divided by radius to give angle in radians
                # TODO work around fudge to get robot pointing north at start (pi/2)
    destQueue.put({'messageType':'sense',
                   'sensedMove' :sourceState.distTravel - sourceState.prevDistTravel,
                   'sensedTheta':theta}) 


      
    
