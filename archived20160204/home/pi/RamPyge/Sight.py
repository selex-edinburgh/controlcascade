from components import Rangefinder, StepMotor
from course import *
import time, threading

### Instantiating an instance of the Sight class will provide you with 
### access to useful methods for examining the chariot's surroundings.
### Use it to find objects, and get their exact positions and bearings
### in relation to the chariot.
class Sight:

    ### This is called whenever the Sight object is created.
    ### Here we just create StepMotor and Rangefinder objects that we
    ### need to get input from the sensors.
    ### cfg -> The list of configuation variables. (list)
    def __init__(self, cfg):
        self.stepMotor = StepMotor(cfg)
        self.rangeFinder = Rangefinder(cfg)
        self.run = True
        self.offsetx = 0
        self.offsety = 10
        

    ### You should call this method after you have initialised the Sight
    ### object, but before you attempt to use any other methods.
    ### This resets the motor to its default starting position.
    def begin(self):
        self.stepMotor.move(0)
        time.sleep(2)

    ### Scans, finds the next change in distance tha looks like an edge,
    ### reports its position, and stops.
    ### threshold -> how much change to allow before detecting an edge
    ### maxdist -> the maximum distance from which to use readings. (int)
    ### timeout -> how long (s) to keep trying to find one. (int)
    ### returns => list with edge position (int), distance (float) or 0
    def nextEdge(self, threshold, maxdist, timeout):
        stime = time.time()
        self.stepMotor.scan()
        d0, a0 = [-1,-1]
        while time.time()-stime < timeout:
            dist = self.rangeFinder.read()
            angle = self.stepMotor.read()
            if d0 > 0 and abs(d0-dist) > threshold and d0 < maxdist:
                return [a0, d0]
            else:
                d0, a0 = [dist, angle]
        return 0


    ### Finds the next object (surface with distance variance under
    ### the given threshold, and within the given distance) and returns
    ### a new Obstacle.
    ### threshold -> how much change to allow before detecting edges (int)
    ### maxdist -> the maximum distance to search for objects (int)
    ### timeout -> how long (s) to keep trying to find one. (int)
    ### returns => the obstacle if one was found, otherwise 0
    def nextObject(self, threshold, maxdist, timeout):
        stime = time.time()
        while time.time() - stime < timeout:
            a0, d0 = self.nextEdge(threshold, maxdist, timeout)
            a1, d1 = self.nextEdge(threshold, maxdist, timeout)
            if a0 > 0 and a1 > 0:
                return Obstacle([a0,a1,d0,d1])
        return 0

    ### Checks if an object is still where it is expected to be by
    ### scanning between the points given.
    ### obj -> The Obstacle to check for (Obstacle)
    ### posA -> Tne start of the range to check within (int)
    ### posB -> The end of the range to check within (int)
    ### returns => True if the object has not moved, otherwise false
    def checkObject(self, obj, posA, posB):
        threshold = 5
        self.stepMotor.move(posA)
        currangle = posA
        self.stepMotor.scan()
        while currangle < posB:
            dist = self.rangeFinder.read()
            currangle = self.stepMotor.read()
            if abs(obj.dT - dist) > threshold:
                return False
        return True

    ### Scans forward and back once, then returns the distance from the
    ### closest found surface.
    ### returns => the distance from the closest surface.
    def closestObject(self):
        self.stepMotor.move(stepMotor.MIN_ANGLE)
        self.stepMotor.scan()
        mindist = 4000
        mina = -1
        currangle = stepMotor.MIN_ANGLE
        while currangle < stepMotor.MAX_ANGLE:
            dist = self.rangeFinder.read()
            currangle = self.stepMotor.read()
            if dist < mindist:
                mindist = dist
                mina = currangle
        return mina

        
