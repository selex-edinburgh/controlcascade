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
from lib.navigation import *
from lib.sensoractions import *

class SensorState(ObservableState):
    def __init__(self):
        super(SensorState,self).__init__()
        self.sensorID = ''
        self.scanCone = [(0.0)]
        self.timeStamp    = time.time()
        self.isCollision = False
        self.robotPos = (0, 0)
        self.robotHdg = 0
        self.waiting = False
        self.realObject1 = ((300,300),0)
        self.realObject2 = ((-300,300),0)
        self.actions = None
        self.sensorSetup = True
        self.running = 3
        
def sensorControlUpdate(state,batchdata):
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
            state.actions = item['actions']
        elif item['messageType'] == 'reset':
            state.sensorSetup = True

    state.robotPos = (1400,2000)
    state.robotHdg = 0
    state.realObject1 = ((1700,2300),0) #((xCoordinate,yCoordinate),objectRadius)
    state.realObject2 = ((1100,2300),0)
    if state.sensorSetup == True:
        #StepperMotor(bus).reinitialiseToCentreDatum()
        state.sensorSetup = False
    if state.waiting == True:
        if state.running == 1:
            bus = I2C(defaultAddress=4)
            #StepperMotor(bus).moveToAngle(0, 1)
            time.sleep(9.5)
            irStepper = ScanningSensor(IR(bus), StepperMotor(bus), 'irStepper')
            #usServo = ScanningSensor(US(bus), ServoMotor(bus), 'usServo') 

            makeSensor_Triangulate = makeTriangulator(scanningSensor=irStepper, scanAngleWidth=20, scanNo=5, scanSpeed=1, scanningSensor2=irStepper, scanAngleWidth2=20, scanNo2=5, scanSpeed2=1)
            action = makeSensor_Triangulate(realObject1, realObject2)
            state = {'robotPos' : robotPos, 'robotHdg' : robotHdg, 'realObject1' : realObject1, 'realObject2' : realObject2, 'irStepper' : ((0,170),0), 'usServo' : ((0,-170),180)}
            action.run(state)
        elif state.running == 3:
            print actions
            
        elif state.running == 2:
            detection1 = NamedDetectionTuple((326.9556545, 66.57), (0, 170), 0)
            detection2 = NamedDetectionTuple((326.9556545, -66.57), (0, 170), 0)
            angleDiff, posDiff = triangulate(robotPos, robotHdg, realObject1, realObject2, detection1, detection2)
            print angleDiff, posDiff
        
def sensorToTrackTranslator(sourceState, destState, destQueue):
    message = {'messageType':'obstacle',
            'collision': sourceState.isCollision}
    destQueue.put(message)
