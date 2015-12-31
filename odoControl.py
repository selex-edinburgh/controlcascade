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

def odoControlUpdate(state,batchdata):
    state.prevPulseL = state.totalPulseL
    state.prevPulseR = state.totalPulseR
    #process items in batchdata
    for item in batchdata:
        if item['messageType'] == 'control':
            pass
        elif item['messageType'] == 'sense':
            state.totalPulseL += item['pulseL']
            state.totalPulseR += item['pulseR']

    #can get state.totalPulseL, state.totalPulseR from i2c here
    #can account for any rollover here
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



########### stub test routine

testCounter = 1.0
testWorkerRunning = False

def testOdoObsTranStub( sourceState, destState, destQueue ):
    def testWorker():
        global testCounter
        demandToMeet = 0.05
        while testWorkerRunning:
            sourceState.demandLR
            destQueue.put({'messageType':'sense',
                           'leftPulses':demandLR[0],
                           'rightPulses':demandLR[1]}) 
            testCounter += 0.0
            time.sleep(0.05)
    global testWorkerRunning, testCounter 
    if not testWorkerRunning :
        th = threading.Thread(target=testWorker)
        th.daemon = True
        testWorkerRunning = True
        th.start()
    testCounter = 1.0
    
      
    
