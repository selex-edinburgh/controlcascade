'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from math import cos, sin, radians, atan2, hypot, degrees
from navigation import *

def triangulate(RobotPos, RobotHdg, RealPole1, RealPole2, Detection1, Detection2):

    
    def angleDifference(RealPole1, RealPole2, DetectionPole1, DetectionPole2):
        RealPole = (RealPole1[0] - RealPole2[0], RealPole1[1] - RealPole2[1])
        DetectionPole = (DetectionPole1[0] - DetectionPole2[0], DetectionPole1[1] - DetectionPole2[1])
        RealPoleAngle = degrees(atan2(RealPole[0],RealPole[1]))
        DetectionPoleAngle = degrees(atan2(DetectionPole[0],DetectionPole[1]))
        AngleDiff = RealPoleAngle - DetectionPoleAngle
        return AngleDiff
    def positionDifference(RealPole1, RealPole2, DetectionPole1, DetectionPole2):
        PosDiff1 = (RealPole1[0] - DetectionPole1[0], RealPole1[1] - DetectionPole1[1])
        PosDiff2 = (RealPole2[0] - DetectionPole2[0], RealPole2[1] - DetectionPole2[1])
        PosDiff = ((PosDiff1[0] + PosDiff2[0])/2,(PosDiff1[1] + PosDiff2[1])/2 )
        return PosDiff

    
    SensorPosOffset1 = Detection1.sensorPosOffset
    SensorHdgOffset1 = Detection1.sensorHdgOffset
    RTheta1 = Detection1.RTheta
    SensorPosOffset2 = Detection2.sensorPosOffset
    SensorHdgOffset2 = Detection2.sensorHdgOffset
    RTheta2 = Detection2.RTheta
    DetectionPole1 = sensorToWorld(RobotPos, RobotHdg, SensorPosOffset1, SensorHdgOffset1, RTheta1)
    DetectionPole2 = sensorToWorld(RobotPos, RobotHdg, SensorPosOffset2, SensorHdgOffset2, RTheta2)
    AngleDiff = angleDifference(RealPole1, RealPole2, DetectionPole1, DetectionPole2)
    RobotHdg = RobotHdg + AngleDiff
    DetectionPole1 = sensorToWorld(RobotPos, RobotHdg, SensorPosOffset1, SensorHdgOffset1, RTheta1)
    DetectionPole2 = sensorToWorld(RobotPos, RobotHdg, SensorPosOffset2, SensorHdgOffset2, RTheta2)
    PosDiff = positionDifference(RealPole1, RealPole2, DetectionPole1, DetectionPole2)
    return AngleDiff, PosDiff

if __name__ == '__main__':
    from collections import namedtuple
    NamedDetectionTuple = namedtuple('NamedDetectionTuple', 'RTheta sensorPosOffset sensorHdgOffset')
    
    RobotPos = (1400, 2000)
    RobotHdg = 0
    SensorPosOffset = (0,170)
    SensorHdgOffset = 0
##    Detection1 = ((424, 45), (0,170), 0)
##    Detection2 = ((424,-45), (0,170), 0)
    RealPole1 = (1700, 2300)
    RealPole2 = (1100, 2300)
    TrueRobotPos = (1400, 2000)
    TrueRobotAngle = 0
    TrueAngleError = 10
    TruePosError = (80, -80)

    ErrorRobotPos = (TrueRobotPos[0] - TruePosError[0],TrueRobotPos[1] - TruePosError[1])
    print 'that', ErrorRobotPos
    ErrorRobotAngle = TrueRobotAngle - TrueAngleError

    (R1, theta1) = worldToSensor(TrueRobotPos, TrueRobotAngle, SensorPosOffset, SensorHdgOffset, RealPole1)
    (R2, theta2) = worldToSensor(TrueRobotPos, TrueRobotAngle, SensorPosOffset, SensorHdgOffset, RealPole2)

        
    print (R1, theta1)
    print (R2, theta2)
    #RobotPos = (RobotPos[0] + PosDiff[0], RobotPos[1] + PosDiff[1])

    testDetection1 = NamedDetectionTuple((R1,theta1),SensorPosOffset,SensorHdgOffset )
    testDetection2 = NamedDetectionTuple((R2,theta2),SensorPosOffset,SensorHdgOffset )

    AngleDiff, PosDiff = triangulate(ErrorRobotPos, ErrorRobotAngle, RealPole1, RealPole2, testDetection1, testDetection2)

    print AngleDiff
    print PosDiff
    
