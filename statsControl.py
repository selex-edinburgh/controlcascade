import math
import threading
import time
import csv
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator


class StatsState(ObservableState):
    def __init__(self):
        super(StatsState,self).__init__()
        self.time = 0
        self.average = 0
        self.max = 0
        self.min = 0
        self.length = 0
        self.variance = 0
        self.motorCmds = {}
        self.rcCmds = (0.0, 0.0)
        self.odoReading = (0.0, 0.0)
        self.time = time.time()
                
def statsControlUpdate(state, batchdata):
    for item in batchdata:

        if item['messageType'] == 'time':
            if 'sourceState' in item:
                pass
            if 'delta' in item:
                pass
    
        if item['messageType'] == 'motor':
            state.rcCmds = (item['rcFwd'], item['rcTurn'])
  

        if item['messageType'] == 'odo':
            state.odoReading = (item['pulseL'], item['pulseR'])
            
   # if item['delta'] in batchdata:
    #    state.max = max(item['delta']['control'] )
     #   state.min = min(item['delta']['control'] for item in batchdata)
      #  state.average = sum(item['delta']['control'] for item in batchdata) / len(batchdata)
       # state.variance = sum((state.average - item['delta']['control']) ** 2 for item in batchdata) / len(batchdata)
        #state.length = len(batchdata)
                
    
    state.time = time.time()
    f = open("motorOdo1.txt", "a")
    f.write ((str(state.time)) + "," )
    f.write ((str(state.rcCmds[0])) + ",")
    f.write ((str(state.rcCmds[1])) + ",")
    f.write ((str(state.odoReading[1])) + ",")
    f.write ((str(state.odoReading[0])) + "," + "\n")

def toStatsTranslator(sourceState, destState, destQueue):
    timeNow = time.time()
    deltaTs = {}
    
    for key, value in sourceState.timeStampFlow.iteritems():
      deltaTs[key] =  timeNow - value
      
    message = {'messageType': 'time',
                'timeStamp': sourceState.timeStampFlow,
                'delta': deltaTs,
                'sourceState': sourceState.__class__.__name__}
               
    destQueue.put(message)
    
def statsToVisualTranslator(sourceState, destState, destQueue):
    message = {'messageType': 'stats',
                'average':sourceState.average,
                'max':sourceState.max,
                'min':sourceState.min,
                'length':sourceState.length,
                'variance':sourceState.variance
                }
    destQueue.put(message)