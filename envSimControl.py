'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.arcnode import ArcNodeObserverTranslator

class EnvSimState(ObservableState):
    def __init__(self):
        super(EnvSimState,self).__init__()
        self.poleList = [(1300,600),(1500,600),(1700,600),(3100,600),(3300,600),
                        (3500,600),(1900,1500),(2100,1500),(2300,1500),(2500,1500),(2700,1500),
                        (2900,1500),(1300,2400),(1500,2400),(1700,2400),(3100,2400),
                        (3300,2400),(3500,2400),(2000,3300),(2200,3300),(2400,3300),
                        (2600,3300),(2800,3300),(1400,6150),(3400,6150)]
        self.wallList = [
            (1200,0, 1200,2400), (1200,2400, 0,2400),
            (0,2400, 0,7200), (0,7200, 4800,7200),
            (4800,7200, 4800,2400), (4800,2400, 3600,2400),
            (3600,2400, 3600,0), (3600,0, 1200,0)]
        self.barrelList = []
        self.barrierList = [(400,7200,0,6800), (2400,0,2400,2400), (4400,7200,4800,6800)]
        self.rampList = []
        self.doorList = []
        self.goalList = [(600,2400,0,3000), (4200,2400,4800,3000)]
        self.ballList = [(600,3000),(4200,3000)]

def envSimControlUpdate(state, batchdata):

    for item in batchdata:
        if item['messageType'] == 'control':
            pass

        elif item['messageType'] == 'sense':

            pass

    if len(batchdata) == 0: return

def envSimToSensorTranslator(sourceState, destState, destQueue):
    message = {'messageType':'sense',
               'sensedPole':sourceState.poleList,
               'sensedWall':sourceState.wallList}
    destQueue.put(message)

def envToVisualTranslator(sourceState, destState, destQueue):
    message = {'messageType':'obstacle',
               'poleList':sourceState.poleList,
               'wallList':sourceState.wallList,
               'barrelList':sourceState.barrelList,
               'barrierList':sourceState.barrierList,
               'rampList':sourceState.rampList,
               'doorList':sourceState.doorList,
               'goalList':sourceState.goalList,
               'ballList':sourceState.ballList,
               'barrierList': sourceState.barrierList}
    destQueue.put(message)

def envToScanSimControl(sourceState, destState, destQueue):
    message = {'messageType': 'obstacle',
                'poleList': sourceState.poleList
}
    destQueue.put(message)
