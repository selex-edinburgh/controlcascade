'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from math import cos, sin, radians, atan2, hypot, degrees
from navigation import *

def angleDifference(RealPole1, RealPole2, DetectionPole1, DetectionPole2):
    RealPole = (RealPole1[0] - RealPole2[0], RealPole1[1] - RealPole2[1])
    DetectionPole = (DetectionPole1[0] - DetectionPole2[0], DetectionPole1[1] - DetectionPole2[1])
    RealPoleAngle = degrees(atan2(RealPole))
    DetectionPoleAngle = degrees(atan2(DetectionPole))
    AngleDiff = RealPoleAngle - DetectionPoleAngle
    return (AngleDiff)

def triangulate(RobotPos, RobotHdg, SensorPosOffset,SensorHdgOffset, RealPole1, RealPole2, Detection1, Detection2):
    SensorPosOffset1 = Detection1.sensorPosOffset
    SensorHdgOffset1 = Detection1.sensorHdgOffset
    
    DetectionPole1 = sensorToWorld(RobotPos, RobotHdg, SensorPosOffset1, SensorHdgOffset1, Detection1)
    DetectionPole2 = sensorToWorld(RobotPos, RobotHdg, SensorPosOffset2, SensorHdgOffset2, Detection2)
    AngleDiff = angleDifference(RealPole1, RealPole2, DetectionPole1, DetectionPole2)
    RobotHdg = RobotHdg + AngleDiff
    DetectionPole1 = sensorToWorld(RobotPos, RobotHdg, SensorPosOffset, SensorHdgOffset, Detection1)
    DetectionPole2 = sensorToWorld(RobotPos, RobotHdg, SensorPosOffset, SensorHdgOffset, Detection2)
    PosDiff1 = (RealPole1 -DetectionPole1)
    PosDiff2 = (RealPole2 - DetectionPole2)
    PosDiff = (PosDiff1 + PosDiff2)/2

    return AngleDiff, PosDiff

if __name__ == '__main__':
    RobotPos = None
    RobotHdg = None
    SensorPosOffset = None
    SensorHdgOffset = None
    Detection1 = None
    Detection2 = None
    RealPole1 = None
    RealPole2 = None
    AngleDiff, PosDiff = triangulate(RobotPos, RobotHdg, RealPole1, RealPole2, Detection1, Detection2)
    RobotPos = (RobotPos[0] + PosDiff[0], RobotPos[1] + PosDiff[1])
