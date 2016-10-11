
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
