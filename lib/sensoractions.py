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
import sys
import time
import math
import numpy
import smbus
from collections import namedtuple
from navigation import *

NamedDetectionTuple = namedtuple('NamedDetectionTuple', 'rTheta sensorPosOffset sensorHdgOffset')

'''
Section 2
Amber Block
'''
def _readData(i2cBus, control):
    rxBytes = i2cBus.read(control, 6)  #Read 6 Bytes                
    angle = rxBytes[0]*256 + rxBytes[1]     #Add High and Low Bytes
    distance = rxBytes[2]*256 + rxBytes[3]  #Add High and Low Bytes
    scanNum = rxBytes[4]
    scanDirection = rxBytes[5]
    return angle, distance, scanNum, scanDirection

class I2C(object):
    def __init__(self, defaultAddress=4):
        # set up I2C serial link
        self.defaultAddress = defaultAddress
        self.defaultBusIndex = 1                #There are two I2C SMbus available on the R-Pi
        self.bus = smbus.SMBus(self.defaultBusIndex) # Create Samba Bus Client
                    
    '''
        The WRITE_I2C function sends a message from the R-Pi master to the
        Sensors Board slave
        The message contains the Address with READ/WRITE bit(0) followed by 4 Bytes.
        These 4 Bytes are:   control, numBytes, txByte[0], txByte[1]
         (For a WRITE command the parameter numBytes is inserted by the R-Pi)
    '''
    def write(self, control, txBytes, address = None):
        if address == None:
            address = self.defaultAddress
        try:
            self.bus.write_block_data(address, control, txBytes)		
        except Exception as err:
            print err       #error does not work as it's a write command
            print "Failed to write to the bus"
    
    '''
        The READ_I2C function sends a message from the R-Pi master to the
        Sensors Board Slave requesting the Sensors Board to send it data.
        The R-Pi sends address with READ/WRITE bit(0) followed by control Byte.
        The Sensors Board prepares the data and waits.
        The R-Pi resends address with READ/WRITE bit(1) and reads back 4 Bytes.
        These 4 Bytes are rxByte[0], rxByte[1], rxByte[2], rxByte[3]
    '''
    def read(self, control, numBytes, address = None):
        if address == None:
            address = self.defaultAddress
        try:
            rxBytes = self.bus.read_i2c_block_data(address, control, numBytes)
            return rxBytes
        except Exception as err:
            print err
            print "Failed to write to the bus"

'''
Section 3
Amber Block
'''
class Motor(object):
    def __init__(self):
        pass

    def moveToAngle(self, angleStart, angleEnd, speed):
        pass

    def moveBetweenTwoAngles(self, speed):
        pass

    def getCurrentAngle(self):
        pass

    def getNearestAngle(self):
        pass

class Sensor(object):
    def __init__(self):
        pass

    def getCurrentRange(self):
        pass

    def getNearestRange(self):
        pass
    
    def getCurrentScanNumber(self):
        pass

    def getNearestScanNumber(self):
        pass

class Action(object):
    def __init__(self):
        pass

    def run(self, state):
        pass

'''
Section 4
Green Block
'''
class StepperMotor(Motor):
    def __init__(self, i2cBus=None):
        self.i2cBus = i2cBus or I2C(defaultAddress=4)
        self.steprFixedAngle = 90     # +/- degrees (0.1 deg accuracy available)
        self.steprScanAngleLt = 45   # +/- degrees (to 1 deg accuracy)
        self.steprScanAngleRt = -45  # +/- degrees (to 1 deg accuracy)
        self.servoFixedAngle = 0     # +/- degrees (0.1 deg accuracy available)
        self.servoScanAngleLt =  45  # +/- degrees (to 1 deg accuracy)
        self.servoScanAngleRt = -45  # +/- degrees (to 1 deg accuracy)
        
        # Calibration values        
        self.steprScaling= 11.32  #stepper movement mechanical scaling in bits/degree
        self.steprDatum = 3200    #offset of Stepper Motor micro switch datum in steps
        self.servoScaling = 9.26  #servo movement scaling in bits/degree
        self.servoOffset = 8.1    #servo shaft offset from chassis centreline in degrees
        self.IRslope = 1          #slope of calibration straight line "m"
            
        self.IRoffset = 0         #offset of calibration straight line "c"
    
    def reinitialiseToCentreDatum(self):
        #Convert stepperDatum to Hi & Lo Bytes steps for transmission
        control = 37 #Stepper Reinitialise (32+4+Speed 1)
        txBytes = [0,0,0,0] #Define txBytes as 2 Bytes
        txBytes[0] = int(self.steprDatum/256)                #stepperDatum Hi Byte
        txBytes[1] = int(self.steprDatum - txBytes[0]*256)   #stepperDatum Lo Byte
        txBytes[2] = 0                                       #number of scans to perform
        txBytes[3] = 4                                       #Dummy Test Value. Will be removed in a future patch
        print 'reinitialise', txBytes[0], txBytes[1], txBytes[2], txBytes[3]
        self.i2cBus.write(control, txBytes)            #sent to sensors

    def moveToAngle(self, angle, speed=1):
        if speed <1 or speed >3:
            return "Invalid speed entered:" + speed + ". Make value from 1-3"
        control = 40 + speed #if control >=41 and control <=43:       #Stepper Motor Go To Fixed Angle
        #Convert steprFixedAngle to Hi & Lo Bytes steps for transmission
        steprFixedAngleScaled = angle*self.steprScaling + 2048  #scale for steps/deg & add centre offset
        min(max(round(steprFixedAngleScaled),0),4095)
        txBytes = [0,0,0,0] #Define txBytes as 2 Bytes
        txBytes[0] = int(steprFixedAngleScaled/256)              #steprFixedAngle Hi Byte
        txBytes[1] = int(steprFixedAngleScaled - txBytes[0]*256) #steprFixedAngle Lo Byte
        txBytes[2] = 0                                           #number of scans to perform
        txBytes[3] = 4                                           #Dummy Test Value. Will be removed in a future patch
        #print txBytes[0],txBytes[1],int(self.steprFixedAngle), steprFixedAngleScaled #print to screen
        self.i2cBus.write(control, txBytes)          #sent to sensors

    def moveBetweenTwoAngles(self, angleStart, angleEnd, numOfScans, speed=1):
        if speed <1 or speed >3:
            return "Invalid speed entered:" + speed + ". Make value from 1-3"
        control = 44 + speed #if control >=45 and control <=47:  #Stepper Motor Scan Between Two Angles
        #Convert steprScanAngleLt & Rt to Byte steps for transmission
        steprScanAngleLtScaled = angleStart*self.steprScaling + 2048  #scale for steps/deg & add offset
        steprScanAngleRtScaled = angleEnd*self.steprScaling + 2048  #scale for steps/deg & add offset
        min(max(round(steprScanAngleLtScaled),0),4095)
        min(max(round(steprScanAngleRtScaled),0),4095)
        txBytes = [0,0,0,0] #Define txBytes as 2 Bytes
        txBytes[0] = int(steprScanAngleLtScaled/16)        #convert to Byte (0 to 255)
        txBytes[1] = int(steprScanAngleRtScaled/16)        #convert to Byte (0 to 255)
        txBytes[2] = numOfScans                            #number of scans to perform
        txBytes[3] = 4                                     #Dummy Test Value. Will be removed in a future patch
        print 'moveBetweenTwoAngles',(txBytes[0],txBytes[1],txBytes[2],txBytes[3])            #print to screen
        self.i2cBus.write(control, txBytes)    #sent to sensors

    def getCurrentAngle(self):
        angle, __distance, __scanNum, __direction = _readData(self.i2cBus, 112)
        return (angle-2048)/11.32 #remove offset & scale for steps/deg

    def getNearestAngle(self):
        angle, __distance, __scanNum, __direction = _readData(self.i2cBus, 116)
        return (angle-2048)/11.32 #remove offset & scale for steps/deg

'''
Section 5
Green Block
'''
class IR(Sensor):
    def __init__(self, i2cBus=None):
        self.i2cBus = i2cBus or I2C(defaultAddress=4)

    def getCurrentIR_RangeStepperAngle(self):
        angle, distance, scanNum, direction = _readData(self.i2cBus, 112)
        # Select and Scale Sensor Readings for rangeIR and AngleIR
        angleIR = (angle-2048)/11.32 #remove offset & scale for steps/deg
        rangeIR = (distance*10)      #Scale IR sensor Range
        scanNumIR = scanNum
        directionIR = direction
        return angleIR, rangeIR, scanNumIR, directionIR

    def getNearestIR_RangeStepperAngle(self):
        angle, distance, scanNum, direction = _readData(self.i2cBus, 116)
        angleIR = (angle-2048)/11.32 #remove offset & scale for steps/deg
        rangeIR = distance*10        #Scale IR sensor Range
        scanNumIR = scanNum
        directionIR = direction
        return angleIR, rangeIR, scanNumIR, directionIR

    def getCurrentRange(self):
        __angle, distance, __scanNum, __direction = _readData(self.i2cBus, 112)
        return distance*10        #Scale IR sensor Range

    def getNearestRange(self):
        __angle, distance, __scanNum, __direction = _readData(self.i2cBus, 116)
        return distance*10        #Scale IR sensor Range
    
    def getCurrentScanNumber(self):
        __angle, __distance, scanNum, direction = _readData(self.i2cBus, 112)
        return scanNum, direction

    def getNearestScanNumber(self):
        __angle, __distance, scanNum, direction = _readData(self.i2cBus, 116)
        return scanNum, direction

'''
Section 6
Amber Block
'''
def makeTriangulate(scanAction1, scanAction2):
    return TriangulateAction(scanAction1, scanAction2)

def makeScan(scanningSensor, coordinate, scanAngleWidth, scanNo, scanSpeed):
    return ScanningSensorAction(scanningSensor, coordinate,scanAngleWidth,scanNo,scanSpeed)

def makeTriangulator(scanningSensor, scanAngleWidth, scanNo, scanSpeed, scanningSensor2, scanAngleWidth2, scanNo2, scanSpeed2):
    def create(coordinate1, coordinate2, scanningSensor1 = scanningSensor, scanningSensor2 = scanningSensor2, scanAngleWidth1=scanAngleWidth, scanAngleWidth2 = scanAngleWidth2, scanNo1=scanNo, scanNo2=scanNo2, scanSpeed1=scanSpeed, scanSpeed2=scanSpeed2):
        scanAction1 = ScanningSensorAction(scanningSensor1, coordinate1, scanAngleWidth1, scanNo1, scanSpeed1)
        scanAction2 = ScanningSensorAction(scanningSensor2, coordinate2, scanAngleWidth2, scanNo2, scanSpeed2)
        return makeTriangulate(scanAction1, scanAction2)
    return create

'''
Section 7
Green Block

This function takes the R-Theta coordinates of the two known objects detected by the IR sensor.
It then calculates the XY position of the chariot in arean corrdinates and the heading of the chariot within the arena.
This information is used to update the position and the heading of the chariot in the arena.
The putput is the X & Y error in mm and the heading error in degrees.
'''
def triangulate(robotPos, robotHdg, realObject1, realObject2, detection1, detection2):  # robot position and robot heading from odometer readings,
                                                                                            #real objects 1 & 2 arena coordinates,
                                                                                            #detected objects 1 & 2 R-Theta values with sensor offsets for position and heading
    def angleDifference(realObject1, realObject2, detectionObject1, detectionObject2):
        realObjectsVector = (realObject1[0] - realObject2[0], realObject1[1] - realObject2[1])
        detectionObjectsVector = (detectionObject1[0] - detectionObject2[0], detectionObject1[1] - detectionObject2[1])
        realObjectAngle = degrees(atan2(realObjectsVector[0],realObjectsVector[1]))
        detectionObjectAngle = degrees(atan2(detectionObjectsVector[0],detectionObjectsVector[1]))
        angleDiff = realObjectAngle - detectionObjectAngle
        return angleDiff
    def positionDifference(realObject1, realObject2, detectionObject1, detectionObject2):
        posDiff1 = (realObject1[0] - detectionObject1[0], realObject1[1] - detectionObject1[1])
        posDiff2 = (realObject2[0] - detectionObject2[0], realObject2[1] - detectionObject2[1])
        # TODO make check to see if difference in error is too great. At that point just use one diffference with smallest error. Otherwise take average of both differences
        posDiff = ((posDiff1[0] + posDiff2[0])/2,(posDiff1[1] + posDiff2[1])/2 )
        return posDiff
    def expectedDetectionOnObject(robotPos, realObject):
        # points on perimeter of realObject1,2
        print 'realObj', realObject[0], realObject[1]
        roToRobotX = realObject[0][0] - robotPos[0]
        roToRobotY = realObject[0][1] - robotPos[1]
        dist = math.hypot(roToRobotX, roToRobotY)
        roToPerimiterX = (realObject[1] * roToRobotX) / dist
        roToPerimiterY = (realObject[1] * roToRobotY) / dist
        print 'roToPerimiterX', roToPerimiterX
        print 'roToPerimiterY', roToPerimiterY
        pointOnROX = realObject[0][0] - roToPerimiterX
        pointOnROY = realObject[0][1] - roToPerimiterY
        print 'pointOnRO',(pointOnROX,pointOnROY)
        return (pointOnROX,pointOnROY)
    
    sensorPosOffset1 = detection1.sensorPosOffset   # position of sensor 1 on the chariot top
    sensorHdgOffset1 = detection1.sensorHdgOffset   # heading of sensor 1 on the chariot top with respect to forwards
    rTheta1 = detection1.rTheta
    sensorPosOffset2 = detection2.sensorPosOffset   # position of sensor 2 on the chariot top
    sensorHdgOffset2 = detection2.sensorHdgOffset   # heading of sensor 2 on the chariot top with respect to forwards
    rTheta2 = detection2.rTheta
    detectedObjectPos1 = sensorToWorld(robotPos, robotHdg, sensorPosOffset1, sensorHdgOffset1, rTheta1) # function returns X, Y of detected object 1 in arena coords from sensor 1,
                                                                                                            #using robot position and heading calculated from the odometers 
    detectionObject2 = sensorToWorld(robotPos, robotHdg, sensorPosOffset2, sensorHdgOffset2, rTheta2)   # function returns X, Y of detected object 2 in arena coords from sensor 2,
                                                                                                            #using robot position and heading calculated from the odometers 

    pointOnRO1 = expectedDetectionOnObject((robotPos[0]+sensorPosOffset1[0],robotPos[1]+sensorPosOffset1[1]) , realObject1) # correction due to radius of real object (if pole) for real object 1
    pointOnRO2 = expectedDetectionOnObject((robotPos[0]+sensorPosOffset2[0],robotPos[1]+sensorPosOffset2[1]) , realObject2) # correction due to radius of real object (if pole) for real object 2
    
    angleDiff = angleDifference(pointOnRO1, pointOnRO2, detectionObject1, detectionObject2) # calculates the angle difference between the real object position and the detected object position
    robotHdg = robotHdg + angleDiff                                                         # applies difference in angle to chariot hdg
    detectionObject1 = sensorToWorld(robotPos, robotHdg, sensorPosOffset1, sensorHdgOffset1, rTheta1)   #with chariot heading updated, detection object 1 is calculated again to get new position coords
    detectionObject2 = sensorToWorld(robotPos, robotHdg, sensorPosOffset2, sensorHdgOffset2, rTheta2)   #with chariot heading updated, detection object 2 is calculated again to get new position coords
    posDiff = positionDifference(pointOnRO1, pointOnRO2, detectionObject1, detectionObject2)    # calculates the position difference between the real object position and the detection object position
    return angleDiff, posDiff # returns the two calculated error changes to be applied to the current chariots position and heading

'''
Section 8
Green Block
'''
class TriangulateAction(Action):
    def __init__(self, scanAction1, scanAction2):
        super(TriangulateAction, self).__init__()
        self.scanAction1 = scanAction1
        self.scanAction2 = scanAction2
        
        
    def run(self, state):
        print 'robotPos', state['robotPos'], 'robotHdg', state['robotHdg']
##        truePosError = (100, -100)
##        trueAngleError = 10
        robotPos = state['robotPos']
        robotHdg = state['robotHdg']
        realObject1 = self.scanAction1.coordinate
        realObject2 = self.scanAction2.coordinate
##        robotPos = (robotPos[0] - truePosError[0],robotPos[1] - truePosError[1])
##        robotHdg = robotHdg - trueAngleError
        print 'robotPos', robotPos, 'robotHdg', robotHdg
        print'...'
        detection1 = self.scanAction1.run(state)
        print '...'
        detection2 = self.scanAction2.run(state)
        angleDiff, posDiff = triangulate(robotPos, robotHdg, realObject1, realObject2, detection1, detection2)
        print '...'
        print 'angleDiff', angleDiff
        print 'posDiff', posDiff

'''
Section 9
Green Block
'''
class ScanningSensorAction(Action):
    def __init__(self, scanningSensor, coordinate,scanAngleWidth,scanNo,scanSpeed):
        super(ScanningSensorAction, self).__init__()
        self.scanningSensor = scanningSensor
        self.coordinate = coordinate
        self.scanAngleWidth = numpy.abs(scanAngleWidth)
        self.numOfScans = scanNo*2
        self.scanSpeed = scanSpeed
    def run(self, state):
        sensorPosOffset = state[self.scanningSensor.sensorID][0]
        sensorHdgOffset = state[self.scanningSensor.sensorID][1]
        rangeToMid, midAngle = worldToSensor(state['robotPos'], state['robotHdg'], sensorPosOffset, sensorHdgOffset, self.coordinate[0])
        print 'rangeToMid', rangeToMid, 'midAngle', midAngle
        if midAngle >180:
            midAngle = midAngle - 360
        angle1 = midAngle + (self.scanAngleWidth*0.5)
        angle2 = midAngle - (self.scanAngleWidth*0.5)
        print 'angle1', angle1, 'angle2', angle2, self.numOfScans
        self.scanningSensor.scanBetweenTwoAngles(angle1,angle2,self.numOfScans,self.scanSpeed)
        objRangeResults = []
        objAngleResults = []
        currentScanNo, scanDirection = self.scanningSensor.getNearestScanNumber()
        while currentScanNo < self.numOfScans+1:
            currentScanNo, scanDirection = self.scanningSensor.getNearestScanNumber()
            print 'currentScanNo', currentScanNo, 'numOfScans', self.numOfScans
            if currentScanNo != 0:
                previousScanNo = currentScanNo
                while previousScanNo == currentScanNo:
                    currentScanNo, scanDirection = self.scanningSensor.getNearestScanNumber()
                    time.sleep(0.005)
                tempRange = self.scanningSensor.getNearestScanRange()
                tempAngle = self.scanningSensor.getNearestAngle()
                objRangeResults.append(tempRange)
                objAngleResults.append(tempAngle)
                print 'tempRange', tempRange, 'tempAngle', tempAngle
        rangeOfObj = numpy.mean(objRangeResults)
        angleOfObj = numpy.mean(objAngleResults)
        print 'rangeOfObj', rangeOfObj, 'angleOfObj', angleOfObj
        
        self.scanningSensor.scanAtAngle(0, self.scanSpeed)
        time.sleep(3)
        return NamedDetectionTuple((rangeOfObj, angleOfObj), sensorPosOffset, sensorHdgOffset)

'''
Section 10
Green Block
'''
class ScanningSensor(object):
    def __init__(self, sensor, motor, sensorID):
        self.sensor = sensor
        self.motor = motor
        self.sensorID = sensorID
        
    def reinitialise(self):
        self.motor.reinitialiseToCentreDatum()
        
    def scanBetweenTwoAngles(self, angleStart, angleEnd, numOfScans, scanSpeed=1):
        self.motor.moveBetweenTwoAngles(angleStart, angleEnd, numOfScans, scanSpeed)
        
    def scanAtAngle(self, angle, scanSpeed=1):
        self.motor.moveToAngle(angle, scanSpeed)

    def getCurrentAngle(self):
        return self.motor.getCurrentAngle()

    def getNearestAngle(self):
        return self.motor.getNearestAngle()

    def getCurrentScanRange(self):
        return self.sensor.getCurrentRange()
    
    def getNearestScanRange(self):
        return self.sensor.getNearestRange()
    
    def getCurrentScanNumber(self):
        return self.sensor.getCurrentScanNumber()
    
    def getNearestScanNumber(self):
        return self.sensor.getNearestScanNumber()
    
##if __name__ == '__main__':
##    robotPos = (1400,2000)
##    robotHdg = 0
##    realObject1 = ((1900,2500),0) #((xCoordinate,yCoordinate),objectRadius)
##    realObject2 = (( 900,2500),0)
##    running = 2
##    if running == 1:
##        bus = I2C(defaultAddress=4)
##        #StepperMotor(bus).moveToAngle(0, 1)
##        #StepperMotor(bus).reinitialiseToCentreDatum()
##        #time.sleep(10)
##        irStepper = ScanningSensor(IR(bus), StepperMotor(bus), 'irStepper')
##        #usServo = ScanningSensor(US(bus), ServoMotor(bus), 'usServo')
##        makeSensor_Triangulate = makeTriangulator(scanningSensor=irStepper, scanAngleWidth=20, scanNo=5, scanSpeed=1, scanningSensor2=irStepper, scanAngleWidth2=20, scanNo2=5, scanSpeed2=1)
##        action = makeSensor_Triangulate(realObject1, realObject2)
##        state = {'robotPos' : robotPos, 'robotHdg' : robotHdg, 'irStepper' : ((0,170),0), 'usServo' : ((0,-170),180)}
##        action.run(state)
##    elif running == 2:
####        detection1 = NamedDetectionTuple((326.9556545, 66.57), (0, 170), 0)
####        detection2 = NamedDetectionTuple((326.9556545, -66.57), (0, 170), 0)
##        detection1 = NamedDetectionTuple((599.0826320, 56.57), (0, 170), 0)
##        detection2 = NamedDetectionTuple((599.0826320, -56.57), (0, 170), 0)
##        angleDiff, posDiff = triangulate(robotPos, robotHdg, realObject1, realObject2, detection1, detection2)
##        print angleDiff, posDiff
