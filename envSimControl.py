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
        self.poleList = [(1300,600),(1500,600),(1700,600),(3100,600),(3300,600),(3500,600),
                         (1900,1500),(2100,1500),(2300,1500),(2500,1500),(2700,1500),(2900,1500),
                         (1300,2400),(1500,2400),(1700,2400),(3100,2400),(3300,2400),(3500,2400),
                         (2000,3300),(2200,3300),(2400,3300),(2600,3300),(2800,3300),
                         (1400,6150),(3400,6150)]
##        self.poleList = [(1265,50),(1550,50),(1820,50),(2980,50),(3265,50),(3535,50),
##                         (1265,620),(1550,620),(1820,620),(2980,620),(3265,620),(3535,620),
##                         (1820,1505),(2095,1505),(2310,1505),(2490,1505),(2705,1505),(2980,1505),
##                         (1265,2390),(1550,2390),(1820,2390),(2980,2390),(3265,2390),(3535,2390)]
        self.wallList = [
            (1200,0, 1200,2400), (1200,2400, 0,2400),
            (0,2400, 0,7200), (0,7200, 4800,7200),
            (4800,7200, 4800,2400), (4800,2400, 3600,2400),
            (3600,2400, 3600,0), (3600,0, 1200,0)]
        self.barrelList = [(1100,5420,60,25),(3100,5420,60,25)]
        self.barrierList = [(400,7200,0,6800), (2400,0,2400,2400), (4400,7200,4800,6800)]
        self.rampList = [(2150,5900,50,120)]
        self.paddleList = [(250,5550,8,50),(3970,5550,8,50)]
        self.goalList = [(800,2600,200,3200,0,2400), (4000,2600,4600,3200,4800,2400)]
        self.ballList = [(800,3200),(4000,3200)]

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
               'paddleList':sourceState.paddleList,
               'goalList':sourceState.goalList,
               'ballList':sourceState.ballList,
               'barrierList': sourceState.barrierList}
    destQueue.put(message)

def envToScanSimControl(sourceState, destState, destQueue):
    message = {'messageType': 'obstacle',
                'poleList': sourceState.poleList
}
    destQueue.put(message)
