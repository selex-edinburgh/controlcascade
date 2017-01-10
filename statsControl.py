'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import math
import threading
import time
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from plumbing.observablestate import ObservableState
from plumbing.arcnode import ArcNodeObserverTranslator

try:        # delete log file
    os.rename('loopStats.txt','log/%s.old' %time.time())
    os.remove('loopStats.txt')
except OSError:
    pass

class StatsState(ObservableState):
    def __init__(self):
        super(StatsState,self).__init__()
        self.time = 0
        self.average = 0
        self.max = 0
        self.min = 0
        self.length = 0
        self.variance = 0
        self.counter = 0

def statsControlUpdate(state, batchdata):

    f = open('loopStats.txt','a')

    for item in batchdata:
        if item['messageType'] == 'time':
            if 'sourceState' in item:
                pass
            if 'delta' in item:
                pass
    try:
        state.max = max(item['delta']['control'] for item in batchdata)
        state.min = min(item['delta']['control'] for item in batchdata)
        state.average = sum(item['delta']['control'] for item in batchdata) / len(batchdata)
        state.variance = sum((state.average - item['delta']['control']) ** 2 for item in batchdata) / len(batchdata)
        state.length = len(batchdata)
        #print "success"
    except:
        pass
        #print "stats error"

    if state.max < 0.5:
        print >> f, time.time(), ",", state.average,",",state.max,",",state.min
    f.close()
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
