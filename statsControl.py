import math
import threading
import time

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
      
        
def statsControlUpdate(state, batchdata):
    for item in batchdata:
        if item['messageType'] == 'time':
            if 'sourceState' in item:
                #print "State:", item['sourceState']
                pass
            if 'delta' in item:
               # print "Latency:", item['delta']['control']
                pass

    state.max = max(item['delta']['control'] for item in batchdata)
    state.min = min(item['delta']['control'] for item in batchdata)
    state.average = sum(item['delta']['control'] for item in batchdata) / len(batchdata)
    state.variance = sum((state.average - item['delta']['control']) ** 2 for item in batchdata) / len(batchdata)
    state.length = len(batchdata)
    
def toStatsTranslator(sourceState, destState, destQueue):
    timeNow = time.time()
    deltaTs = {}
    for key, value in sourceState.timeStampFlow.iteritems():
      deltaTs[key] =  timeNow - value
   # print sourceState.__class__.__name__
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