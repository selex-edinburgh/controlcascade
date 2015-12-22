# -*- coding: utf-8 -*-
import time
import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

odoState = ObservableState()
odoState.demandLR = (0.0,0.0)
odoState.timeStamp    = time.time()
odoState._mmPerPulse = 1.0  

def odoControlUpdate(state,batchdata):
    #process items in batchdata
    for item in batchdata:
        if item['messageType'] == 'control':
            pass
        elif item['messageType'] == 'sense':
            pass


def odoToTrackTranslator( sourceState, destState, destQueue ):
    #todo message = {'messageType':'sense','sensedPos':trackUnitsToMm(sourceState.currentPos)}
    destQueue.put(None)



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
    
      
    
