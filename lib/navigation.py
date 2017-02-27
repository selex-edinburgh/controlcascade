'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
from math import cos, sin, radians, atan2, hypot, degrees

class Waypoint:
    def __init__(self, x = 0, y = 0, waitPeriod = 0, actions = None):
        self.x = x
        self.y = y
        self.waitPeriod = waitPeriod
        self.actions = actions
    def getPosition(self):
        return (self.x,self.y)
    def angleTo_Degrees(self, other):
        return degrees(atan2( other.x - self.x , other.y - self.y ))
    
class WaypointTypeEnum:
    CONTINUOUS = 1
    WAITING = 2

class WaypointManager:
    waitPeriod = 20
    waypointType = WaypointTypeEnum.CONTINUOUS
    @staticmethod
    def createWaypoint(x, y, wpType = waypointType):
        return Waypoint(x, y, 0 if wpType == WaypointTypeEnum.CONTINUOUS else WaypointManager.waitPeriod)
    @staticmethod
    def setWaitPeriod(wp):  
        WaypointManager.waitPeriod = wp
    @staticmethod
    def setWaypointType(wpt):
        WaypointManager.waypointType = wpt

def axisRotation( pos, theta ):
    return ( pos[0] * cos(theta) + pos[1] * sin(theta) , \
             - pos[0] * sin(theta) + pos[1] * cos(theta) )

def degreeAngle(a, b):
    return()

def sensorToWorld(RobotPos, RobotHdg, SensorPosOffset, SensorHdgOffset, RTheta):
    theta1 = RTheta[1] + SensorHdgOffset   #correct object angle for sensor angle offset
    theta2 = radians( 90.0 - theta1 ) # from heading/clock to radians/anticlock
    # now calculate (xs,ys) of object from sensor in Robot relative coordinates
    xs = RTheta[0] * cos( theta2 )
    ys = RTheta[0] * sin( theta2 )
    # calculate (xr, yr) of object from Robot centre
    xr = SensorPosOffset[0] + xs
    yr = SensorPosOffset[1] + ys
    # calculate position relative to robot with north = 0
    posr = axisRotation( (xr, yr),  radians(RobotHdg) )
    # translate result to world coordinates  
    return (posr[0] + RobotPos[0], posr[1] + RobotPos[1])

def worldToSensor(RobotPos, RobotHdg, SensorPosOffset, SensorHdgOffset, ObjectPos):
    # world coordinates translate to robot centre
    posr = (ObjectPos[0] - RobotPos[0], ObjectPos[1] - RobotPos[1])
    # calculate (xr, yr) of object from Robot centre
    (xr, yr) = axisRotation( posr,  - radians(RobotHdg) )
    # now calculate (xs,ys) of object from (xr, yr) of object, relative to sensor
    xs = xr - SensorPosOffset[0]
    ys = yr - SensorPosOffset[1]
    # calculate distance to object from sensor
    R = hypot ( xs, ys )
    # angle of object relative to sensor in radians
    theta2 = atan2 ( ys, xs )
    # from radians/anticlock to heading/clock
    theta1 = (450 - degrees( theta2 )) % 360
    #correct object angle for sensor angle offset
    return(R, theta1 - SensorHdgOffset)

#print sensorToWorld((1,8), 23, (1,5), 180, (1,60))
#print worldToSensor((1,8), 23, (1,5), 180, sensorToWorld((1,8), 23, (1,5), 180, (100,361)))
