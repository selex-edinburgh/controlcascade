'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

'''
Section 1
Green Block
'''
import math
import threading
import time
from plumbing.observablestate import ObservableState
from plumbing.arcnode import ArcNodeObserverTranslator
from lib.navigation import *
from lib.sensoractions import *

class SensorState(ObservableState):
    def __init__(self):
        '''
        Section 2
        Green Block
        '''
        super(SensorState,self).__init__()
        self.sensorID = ''
        self.scanCone = [(0.0)]
        self.isCollision = False
        self.timeStamp = time.time()
        self.robotPos = (0,0)
        self.robotHdg = 0
        self.realObject1 = ((0,0),0)
        self.realObject2 = ((0,0),0)
        self.sensorSetup = False
        self.waiting = False
        self.irStepperOffset = ((0,170),0)
        self.usServoOffset = ((0,-170),180)

        self.running = 1 # To be removed after testing
        
def sensorControlUpdate(state,batchdata):
    '''
    Section 3
    Green Block
    '''
    actions = None
    for item in batchdata:
        if item['messageType'] == 'control':
            pass
        elif item['messageType'] == 'sensedRobot':
            state.robotPos = item['robotPos']
            state.robotHdg = item['robotHdg']
        elif item['messageType'] == 'sense':
            state.sensorID = item['sensorID']
            state.scanCone = item['scanCone']
            state.isCollision = item['collision']
        elif item['messageType'] == 'scan':
            actions = item['actions']
        elif item['messageType'] == 'reset':
            state.sensorSetup = True
    '''
    Section 4
    Green Block
    '''
##    state.robotPos = (1400,2000)
##    state.robotHdg = 0
##    state.realObject1 = ((1700,2300),0) #((xCoordinate,yCoordinate),objectRadius)
##    state.realObject2 = ((1100,2300),0)
    if state.sensorSetup == True:
        StepperMotor(bus).reinitialiseToCentreDatum()
        state.sensorSetup = False
    if state.running == 1:
        if actions != None:
            robotState = {'robotPos' : state.robotPos, 'robotHdg' : state.robotHdg, 'irStepper' : state.irStepperOffset, 'usServo' : state.usServoOffset}
            print actions
            actions.run(robotState) # TODO Put the actions created in routeControl in a list and then change to iterate through them all here
    elif state.running == 2: # For testing
        detection1 = NamedDetectionTuple((326.9556545, 66.57), (0, 170), 0)
        detection2 = NamedDetectionTuple((326.9556545, -66.57), (0, 170), 0)
        angleDiff, posDiff = triangulate(robotPos, robotHdg, realObject1, realObject2, detection1, detection2)
        print angleDiff, posDiff

'''
Section 5
Green Block
'''  
def sensorToTrackTranslator(sourceState, destState, destQueue): # TODO have the angleDiff & posDiff given back to track to be applied.
    message = {'messageType':'obstacle',
            'collision': sourceState.isCollision}
    destQueue.put(message)
