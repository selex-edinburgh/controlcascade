import time, threading, math
from Sight import Sight
from components import *

### The representation of a chariot as a whole, controlling various subcomponents.
class Chariot:

    ### Creates a chariot object but does not start the loop thread. 
    ### To start operation call (Chariot).start() from your Main script.
    def __init__(self):
        self.width, self.length = [31,45]
        self.x, self.y = [160,47]
        self.bearing = 90
        self.speed = 90
            
        self.run = True
        self.cb = ControlBoard()
        self.s = Sight()
        self.od = Odometers(1.31,0,0)

        self.main = threading.Thread(target=self.loop)
        self.main.daemon = True


    ### The main loop. Put all of your instructions and decision logic in here.
    def loop(self):
        while self.run:

            #Get odometer readings and update heading 
            self.bearing += self.od.getHeadingChange()

            #self.bearing += 2
            #print ("Chariot: {}".format(self.bearing))
            #time.sleep(0.01)
            """
            
            #Example: move forward for five seconds and then stop, wait, and go backwards
            self.cb.forward(190)
            time.sleep(5)
            self.cb.stop()
            time.sleep(5)
            self.cb.reverse(60)
            time.sleep(5)
            self.cb.stop()
            time.sleep(5)
            """


    ### Command the robot to make its way towards a given target.
    def go(self, obstacles, targets, ti):
        
        #Check for collisions in the straight path between here and the target
            col = self.collisionCheck(obstacles, targets[ti])
        #If there are no collisions then ensure the bearing matches, then use straight()
            if col:
                #Check whether the bearing matches that of the target
                if self.getBearing(targets[ti]) != 0:
                    self.turn(target)
                #go in a straight line to the target
                self.straight(targets[ti])
        #If there are collisions then use arc()
            else:
                try:
                    self.arc((targets[ti-2],targets[ti-1],targets[ti],targets[ti+1]))
                except:
                    try:
                        self.arc((targets[ti-1],targets[ti-1],targets[ti],targets[ti+1]))
                    except:
                        self.arc((self.x,self.y),(self.x,self.y),targets[ti],targets[ti])
        #If there is no arc then you have a problem


    ### Move the chariot in a straight line to the given target.
    def straight(self, target):
        #get distance that needs to be covered in mm
        distance = 0
        #Make sure it is angled towards the target
        while target.bearing > self.bearing:
            self.cb.right(190)
        self.cb.center()
        while target.bearing < self.bearing:
            self.cb.left(190)
        self.cb.center()
        #get starting odometer reading
        odm = self.od.read()
        self.cb.forward(190)
        while self.od.read() < odm + distance:
            time.sleep(0.1)
        self.cb.stop() #Todo: find out by how much target is overshot


    ### Turn the chariot on the spot to face the given target.
    def turn(self, target):
        #ensure chariot is stationary
        self.cb.stop()
        while target.bearing > self.bearing:
            self.cb.right(190)
        self.cb.center()
        while target.bearing < self.bearing:
            self.cb.left(190)
        self.cb.center()

        
    ### Move the chariot in an arced path from p1 to p2
    def arc(self, p0, p1, p2, p3):
        #Using the four given points, find points on a natural curve between t1 and t2.
        #use these points to find the equation of the curve.
        spline = Spline(p0,p1,p2,p3)
        #Until the chariot gets to p2:
        while (self.x, self.y) != p2:
            self.updateBearing()
            #find the angle between the tangent to the curve at a given point
            # and the current bearing of the chariot.
            tan = spline.tan((self.x,self.y))
            angle = self.getAngle(self.bearing, tan)
            #Turn the chariot while still moving, proportionately to the
            # size of the angle (difference in gradient) :
            # If the chariot is currently turning in the wrong direction:
            if (self.cb.hor < self.cb.CEN and angle > 180) or (self.cb.hor > self.cb.CEN and angle < 180):
                #Turn in the other direction
                self.cb.sleeptime = 0.001
                if angle > 180:
                    self.cb.right(190)
                else:
                    self.cb.left(190)
            # Else if the chariot is turning in the right direction:
            elif (self.cb.hor < self.cb.CEN and angle <= 180) or (self.cb.hor > self.cb.CEN and angle >= 180):
                #If the bearing is correct:
                if angle == 0:
                    #stop turning
                    self.cb.hor = 0  #this is a bit of a naughty way to do it but we don't want easing
            # Else if the chariot is not turning at all:
            else:
                #turn proportionally
                a = 127 + (-(angle-180)/127.0*100)
                if angle > 180:
                    self.cb.left(a)
                else:
                    self.cb.right(a)
            self.cb.sleeptime = self.cb.DEFAULTSLEEP

    ### (Stub) Checks whether the given position is in collision with any defined obstacles.
    def collisionCheck(self, obstacles, position):
        for o in obstacles:
            #do something with what kind of obstacle it is
            #eg check the distance of the origin of a pole from the closest
            # edge of the chariot.
            pass
        return False

    ### Update the current bearing of the chariot
    def updateBearing(self):
        self.bearing += self.od.getHeadingChange()

    ### Get the bearing of a given point from the centre of the chariot.
    ### point -> The point to find a bearing to (tuple)
    ### returns => The relative bearing in degrees. (int)
    def getBearing(self, point):
        return int(math.degrees(getAngle(self.bearing, point)))

    ### Get an angle between the two specified vectors
    ### v1 -> First vector (tuple)
    ### v2 -> Second vector (tuple)
    ### returns => The angle between the vectors in radians (float) 
    def getAngle(self, v1, v2):
        mpmqcostheta = sum(p*q for p,q in zip(v1, v2))
        mp = abs(v1[0])+abs(v1[1])
        mq = abs(v2[0])+abs(v2[1])
        costheta = mpmqcostheta/mp/mq
        return math.acos(costheta)

    ### Get a unit vector between the two specified points.
    ### p1 -> First point (tuple)
    ### p2 -> Second point (tuple)
    ### returns => a unit vector with direction p1 + p2 (tuple)
    def unitVector(self, p1, p2):
        v = tuple(map(lambda a, b: a-b, p1, p2)) #vector from a to b
        uv0, uv1 = [0,0]
        if v[0] != 0: uv0 = v[0]/abs(v[0])
        else: uv0 = v[0]
        if v[1] != 0: uv1 = v[1]/abs(v[1])
        else: uv1 = v[1]
        uv = (uv0,uv1)
        return uv

    ### Starts the chariot operation loop thread.
    def start(self):
        self.main.start()

if __name__ == "__main__":
    c= Chariot()
    c.main.start()



## This will not show up in the documentation as it is probably not required
## for a basic understanding of how to change parts of the application.
## The spline class is here as a container for a function to find a curve
## between the points p1 and p2, the shape of which is affected by the tangents
## from p0 and p3 (a centripetal Catmull-Rom spline.)
class Spline:

    def __init__(self, p0, p1, p2, p3):
        """
        smoothing = 0.5
        self.a = (smoothing*2*p1[0],smoothing*2*p1[1])
        self.b = (smoothing*(-p0[0]+p2[0]),smoothing*(-p0[1]+p2[1]))
        self.c = (smoothing*(2*p0[0]-*p1[0]+4*p2[0]-p3[0]),smoothing*(2*p0[1]-5*p1[1]+4*p2[1]-p3[1]))
        self.d = (smoothing*(-p0[0]+3*p1[0]-3*p2[0]+p3[0]),smoothing*(-p0[1]+3*p1[1]-3*p2[1]+p3[1]))
        self.coeffs = ((a[0],b[0],c[0],d[0]),(a[1],b[1],c[1],d[1]))
        #Honestly I just don't even know anymore
        """
        

    def tan(self, t):
        q = self.a + self.b*t + self.c*t*t + self.d*t*t*t
        
        return math.tan(q)

    
