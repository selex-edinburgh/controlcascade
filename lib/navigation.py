from math import cos, sin, radians, atan2, hypot, degrees

class Waypoint:
    def __init__(self, x = 0, y = 0, waitPeriod = 0):
        self.x = x
        self.y = y
        self.waitPeriod = waitPeriod
    def getPosition(self):
        return (self.x,self.y)
class WaypointTypeEnum:
    CONTINUOUS = 1
    WAITING = 2

class WaypointManager:
    waitPeriod = 5
    waypointType = WaypointTypeEnum.CONTINUOUS
    @staticmethod
    def createWaypoint(x, y):
        return Waypoint(x, y, 0 if WaypointManager.waypointType == WaypointTypeEnum.CONTINUOUS else waitPeriod)
    @staticmethod
    def setWaitPeriod(wp):  
        WaypointManager.waitPeriod = wp
    @staticmethod
    def setWaypointType(wpt):
        WaypointManager.waypointType = wpt

def axisRotation( pos, theta ):
    return ( pos[0] * cos(theta) + pos[1] * sin(theta) , \
             - pos[0] * sin(theta) + pos[1] * cos(theta) )
    

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
