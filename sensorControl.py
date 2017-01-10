'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import math
import threading
import time
from plumbing.observablestate import ObservableState
from plumbing.arcnode import ArcNodeObserverTranslator

class SensorState(ObservableState):
    def __init__(self, scanDist, scanRange):
        super(SensorState,self).__init__()
        self.sensorID = ''
        self.scanRange = 100.0
        self.turnSpeed = 0.0
        self.scanCone = [(0.0)]
        self.timeStamp    = time.time()
        self.isCollision = False
        
def sensorControlUpdate(state,batchdata):
    for item in batchdata:
        if item['messageType'] == 'control':
            pass
            
        elif item['messageType'] == 'sense':
            state.sensorID = item['sensorID']
            state.scanCone = item['scanCone']
            state.isCollision = item['collision']
            
def sensorToTrackTranslator(sourceState, destState, destQueue):
    message = {'messageType':'obstacle',
            'collision': sourceState.isCollision}
    destQueue.put(message)
