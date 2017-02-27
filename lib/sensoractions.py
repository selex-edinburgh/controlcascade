'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import sys
import time
import math
import numpy
import smbus
from collections import namedtuple
from navigation import *

NamedDetectionTuple = namedtuple('NamedDetectionTuple', 'RTheta sensorPosOffset sensorHdgOffset')

def _readAngleAndDistance(i2cBus, control):
    rxBytes = i2cBus.read(control, 4)  #Read 4 Bytes                
    angle = rxBytes[0]*256 + rxBytes[1]     #Add High and Low Bytes
    distance = rxBytes[2]*256 + rxBytes[3]  #Add High and Low Bytes
    return angle, distance

class I2C(object):
    def __init__(self, defaultAddress=4):
        # set up I2C serial link
        self.defaultAddress = defaultAddress
        #self.defaultNumBytesTx = 4                  #I2C Number of Bytes to be Sent
        #self.txBytes = [0]*self.defaultNumBytesTx   #Holds values to be sent
        #self.defaultNumBytesRx = 4                  #I2C Number of Bytes to be Received
        #self.rxBytes = [0]*self.defaultNumBytesRx   #Place for values to be read into
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

class Action(object):
    def __init__(self):
        pass

    def run(self, state):
        pass
    
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
        self.steprDatum = 3300    #offset of Stepper Motor micro switch datum in steps
        self.servoScaling = 9.26  #servo movement scaling in bits/degree
        self.servoOffset = 8.1    #servo shaft offset from chassis centreline in degrees
        self.IRslope = 1          #slope of calibration straight line "m"
            
        self.IRoffset = 0         #offset of calibration straight line "c"
    
    def reinitialiseToCentreDatum(self):
        #Convert stepperDatum to Hi & Lo Bytes steps for transmission
        control = 37 #Stepper Reinitialise (32+4+Speed 1)
        txBytes = [0,0] #Define txBytes as 2 Bytes
        txBytes[0] = int(self.steprDatum/256)                #stepperDatum Hi Byte
        txBytes[1] = int(self.steprDatum - txBytes[0]*256)   #stepperDatum Lo Byte
        #print self.steprDatum, txBytes[0], txBytes[1]
        self.i2cBus.write(control, txBytes)            #sent to sensors

    def moveToAngle(self, speed=1):
        if speed <1 or speed >3:
            return "Invalid speed entered:" + speed + ". Make value from 1-3"
        control = 40 + speed #if control >=41 and control <=43:       #Stepper Motor Go To Fixed Angle
        #Convert steprFixedAngle to Hi & Lo Bytes steps for transmission
        steprFixedAngleScaled = self.steprFixedAngle*self.steprScaling + 2048  #scale for steps/deg & add centre offset
        txBytes = [0,0] #Define txBytes as 2 Bytes
        txBytes[0] = int(steprFixedAngleScaled/256)              #steprFixedAngle Hi Byte
        txBytes[1] = int(steprFixedAngleScaled - txBytes[0]*256) #steprFixedAngle Lo Byte
        #print txBytes[0],txBytes[1],int(self.steprFixedAngle), steprFixedAngleScaled #print to screen
        self.i2cBus.write(control, txBytes)          #sent to sensors

    def moveBetweenTwoAngles(self, angleStart, angleEnd, speed=1):
        if speed <1 or speed >3:
            return "Invalid speed entered:" + speed + ". Make value from 1-3"
        control = 44 + speed #if control >=45 and control <=47:  #Stepper Motor Scan Between Two Angles
        #Convert steprScanAngleLt & Rt to Byte steps for transmission
        steprScanAngleLtScaled = angleStart*self.steprScaling + 2048  #scale for steps/deg & add offset
        steprScanAngleRtScaled = angleEnd*self.steprScaling + 2048  #scale for steps/deg & add offset
        txBytes = [0,0] #Define txBytes as 2 Bytes
        txBytes[0] = int(steprScanAngleLtScaled/16)        #convert to Byte (0 to 255)
        txBytes[1] = int(steprScanAngleRtScaled/16)        #convert to Byte (0 to 255)
        #print(txBytes[0],txBytes[1])            #print to screen
        self.i2cBus.write(control, txBytes)    #sent to sensors

    def getCurrentAngle(self):
        angle, __distance = _readAngleAndDistance(self.i2cBus, 112)
        return (angle-2048)/11.32 #remove offset & scale for steps/deg

    def getNearestAngle(self):
        angle, __distance = _readAngleAndDistance(self.i2cBus, 116)
        return (angle-2048)/11.32 #remove offset & scale for steps/deg

class IR(Sensor):
    def __init__(self, i2cBus=None):
        self.i2cBus = i2cBus or I2C(defaultAddress=4)

    def getCurrentIR_RangeStepperAngle(self):
        angle, distance = _readAngleAndDistance(self.i2cBus, 112)
        # Select and Scale Sensor Readings for rangeIR and AngleIR
        angleIR = (angle-2048)/11.32 #remove offset & scale for steps/deg
        rangeIR = (distance*10)      #Scale IR sensor Range                        
        return angleIR, rangeIR

    def getNearestIR_RangeStepperAngle(self):
        angle, distance = _readAngleAndDistance(self.i2cBus, 116)
        angleIR = (angle-2048)/11.32 #remove offset & scale for steps/deg
        rangeIR = distance*10        #Scale IR sensor Range
        return angleIR, rangeIR

    def getCurrentRange(self):
        __angle, distance = _readAngleAndDistance(self.i2cBus, 112)
        return distance*10        #Scale IR sensor Range

    def getNearestRange(self):
        __angle, distance = _readAngleAndDistance(self.i2cBus, 116)
        return distance*10        #Scale IR sensor Range

def makeTriangulate(scanAction1, scanAction2):
    return TriangulateAction(scanAction1, scanAction2)

##def makeScan(scanningSensor, coordinate, scanAngleWidth, scanNo, scanSpeed):
##    return ScanningSensorAction(scanningSensor, coordinate,scanAngleWidth,scanNo,scanSpeed)

def makeTriangulator(scanningSensor, scanAngleWidth, scanNo, scanSpeed, scanningSensor2, scanAngleWidth2, scanNo2, scanSpeed2):
    def create(coordinate1, coordinate2, scanningSensor1 = scanningSensor, scanningSensor2 = scanningSensor2, scanAngleWidth1=scanAngleWidth, scanAngleWidth2 = scanAngleWidth2, scanNo1=scanNo, scanNo2=scanNo2, scanSpeed1=scanSpeed, scanSpeed2=scanSpeed2):
        scanAction1 = ScanningSensorAction(scanningSensor1, coordinate1, scanAngleWidth1, scanNo1, scanSpeed1)
        scanAction2 = ScanningSensorAction(scanningSensor2, coordinate2, scanAngleWidth2, scanNo2, scanSpeed2)
        return makeTriangulate(scanAction1, scanAction2)
    return create

class TriangulateAction(Action):
    def __init__(self, scanAction1, scanAction2):
        super(TriangulateAction, self).__init__()
        self.scanAction1 = scanAction1
        self.scanAction2 = scanAction2
        
        
    def run(self, state):
        Detection1 = self.scanAction1.run(state)
        Detection2 = self.scanAction2.run(state)
        

class ScanningSensorAction(Action):
    def __init__(self, scanningSensor, coordinate,scanAngleWidth,scanNo,scanSpeed):
        super(ScanningSensorAction, self).__init__()
        self.scanningSensor = scanningSensor
        self.coordinate = coordinate
        self.scanAngleWidth = numpy.abs(scanAngleWidth)
        self.scanNo = scanNo
        self.scanSpeed = scanSpeed
    def run(self, state):
        sensorPosOffset = state[self.scanningSensor.sensorID][0]
        sensorHdgOffset = state[self.scanningSensor.sensorID][1]
        #print state
        rangeToMid, midAngle = worldToSensor(state['robotPos'], state['robotHdg'], sensorPosOffset, sensorHdgOffset, self.coordinate)
        angle1 = midAngle - (self.scanAngleWidth*0.5)
        angle2 = midAngle + (self.scanAngleWidth*0.5)
        print angle1, angle2
        self.scanningSensor.scanBetweenTwoAngles(angle1,angle2,self.scanSpeed)
        objRangeResults = []
        objAngleResults = []
        previousAngle = None
        previousScanDirection = None
        scanDirection = None
        for currentScanNo in xrange(self.scanNo):
            scanState = 1
            tempRange = None
            while scanState < 4:
                currentAngle = self.scanningSensor.getCurrentAngle()
                if previousAngle is not None:
                    diff = previousAngle-currentAngle
                    print "Skip!" if diff < 5 else 'Keep!', currentScanNo, currentAngle, scanDirection if scanDirection else "No Direction", previousScanDirection, scanState
                    if previousAngle != currentAngle and diff < 5:
                        scanDirection = previousAngle > currentAngle
                        if scanDirection is not previousScanDirection:
                            scanState = scanState + 1
                        previousScanDirection = scanDirection
                        previousAngle = currentAngle
                    if tempRange is None or self.scanningSensor.getNearestScanRange() < tempRange:
                        tempRange = self.scanningSensor.getNearestScanRange()
                        tempAngle = self.scanningSensor.getNearestAngle()
            objRangeResults.append(tempRange)
            objAngleResults.append(tempAngle)
        rangeOfObj = numpy.mean(objRangeResults)
        angleOfObj = numpy.mean(objAngleResults)
        #self.scanningSensor.scanAtAngle(1)
        
        return NamedDetectionTuple((rangeOfObj, angleOfObj), sensorPosOffset, sensorHdgOffset)

class ScanningSensor(object):
    def __init__(self, sensor, motor, sensorID):
        self.sensor = sensor
        self.motor = motor
        self.sensorID = sensorID
    def scanBetweenTwoAngles(self, angleStart, angleEnd, scanSpeed=1):
        self.motor.moveBetweenTwoAngles(angleStart, angleEnd, scanSpeed)
        
    def scanAtAngle(self, scanSpeed=1):
        self.motor.moveToAngle(scanSpeed)

    def getCurrentAngle(self):
        return self.motor.getCurrentAngle()

    def getNearestAngle(self):
        return self.motor.getNearestAngle()

    def getCurrentScanRange(self):
        return self.sensor.getCurrentRange()
    
    def getNearestScanRange(self):
        return self.sensor.getNearestRange()

if __name__ == '__main__':
    robotPos = (1400,2000)
    robotHdg = 0
    bus = I2C(defaultAddress=4)
    irStepper = ScanningSensor(IR(bus), StepperMotor(bus), 'irStepper')
    #usServo = ScanningSensor(US(bus), ServoMotor(bus), 'usServo')
    makeSensor_Triangulate = makeTriangulator(scanningSensor=irStepper, scanAngleWidth=10, scanNo=5, scanSpeed=1, scanningSensor2=irStepper, scanAngleWidth2=10, scanNo2=5, scanSpeed2=1)
    action = makeSensor_Triangulate((100, 100), (100, 100))
    state = {'robotPos' : robotPos, 'robotHdg' : robotHdg, 'irStepper' : ((0,170),0), 'usServo' : ((0,-170),180)}
    action.run(state)
