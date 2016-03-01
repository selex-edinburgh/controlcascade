import time, threading, math
from Sight import Sight
from components import *

### The representation of a chariot as a whole, controlling various subcomponents.
class Chariot:

    ### Creates a chariot object but does not start the loop thread. 
    ### To start operation call (Chariot).start() from your Main script.
    def __init__(self, cfg):
        self.width, self.length = [31,45]
        self.x, self.y = [160,47]
        self.bearing = 0
        self.speed = 90
            
        self.run = True
        self.cb = ControlBoard()
        self.s = Sight(cfg)
        self.od = Odometers(cfg,1.31,0,0)

        self.main = threading.Thread(target=self.loop)
        self.main.daemon = True


    ### The chariot position and bearing update loop.
    def loop(self):
        lpos = (self.x,self.y)
        while self.run:

            #Get odometer readings and update heading and position
            disp = self.od.getDisplacementChange()
            x1 = disp * math.sin(self.bearing)
            y1 = disp * math.cos(self.bearing)
            self.x += x1
            self.y += y1
            self.bearing += self.od.getHeadingChange()
            
            time.sleep(0.1)


    ### Command the robot to make its way towards a given target.
    ### target -> the target for the chariot to move towards
    ### obstacles -> the list of obstacles in the current arena
    def go(self, target, obstacles):
        
        #Check for collisions in the straight path between here and the target
            col = self.collisionCheck(obstacles, target)
        #If there are no collisions then ensure the bearing matches, then use straight()
            if not col:
                #Check whether the bearing matches that of the target
                if self.getBearing(target) != 0:
                    self.turn(target)
                #go in a straight line to the target
                self.straight(target)
        #If there are collisions then use arc()
            else:
                try:
                    self.arc(target)
                except:
                    pass
            #If there is no arc then you have a problem


    ### Move the chariot in a straight line to the given target.
    ### target -> the point to move towards (tuple)
    def straight(self, target):
        #get distance that needs to be covered in mm
        distance = abs((target[0]-self.x) + (target[1]-self.y))
        #Make sure it is angled towards the target
        self.turn(target)
        #get starting odometer reading
        odm = self.od.getDisplacementChange()
        self.cb.forward(190)
        while distance > 20:
            self.turn(target)
            odm = self.od.getDisplacementChange()
            bearing = self.bearing
            if self.od.connected == False:
                if math.sin(bearing) < 0:
                    self.x -= math.floor(1 * math.sin(bearing))
                else:
                    self.x += math.ceil(1 * math.sin(bearing))
                if math.cos(bearing) < 0:
                    self.y -= math.floor(1 * math.cos(bearing))
                else:
                    self.y += math.ceil(1 * math.cos(bearing))
            else:
                self.x += math.ceil(odm * math.sin(bearing))
                self.y += math.ceil(odm * math.cos(bearing))
            time.sleep(0.1)
            odm = self.od.read()
            distance = abs(target[0]-self.x) + abs(target[1]-self.y)
            print(distance)
        self.cb.stop() 


    ### Turn the chariot on the spot to face the given target.
    ### target -> the point to move towards (tuple)
    def turn(self, target):
        print(self.getBearing(target))
        if self.od.connected == False:
            self.bearing = self.getBearing(target)
            return
        if self.getBearing(target) > 0:
            self.cb.right(190)
        else:
            self.cb.hor = self.cb.CEN
        if self.getBearing(target) > 180:
            self.cb.left(190)
        else:
            self.cb.hor = self.cb.CEN

        
    ### Move the chariot in an arced path from p1 to p2
    ### target -> the point to move to 
    def arc(self, target):

        """
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
            angle = 20
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
            """

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
        return int(math.degrees(self.getAngle((1,0),self.unitVector((self.x,self.y), point))))

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


"""
## This will not show up in the documentation as it is probably not required
## for a basic understanding of how to change parts of the application.
## The spline class is here as a container for a function to find a curve
## between the points p1 and p2, the shape of which is affected by the tangents
## from p0 and p3 (a centripetal Catmull-Rom spline.)
cl@ss Spline:

    d!ef __init__(self, p0, p1, p2, p3):
        
        smoothing = 0.5
        self.a = (smoothing*2*p1[0],smoothing*2*p1[1])
        self.b = (smoothing*(-p0[0]+p2[0]),smoothing*(-p0[1]+p2[1]))
        self.c = (smoothing*(2*p0[0]-*p1[0]+4*p2[0]-p3[0]),smoothing*(2*p0[1]-5*p1[1]+4*p2[1]-p3[1]))
        self.d = (smoothing*(-p0[0]+3*p1[0]-3*p2[0]+p3[0]),smoothing*(-p0[1]+3*p1[1]-3*p2[1]+p3[1]))
        self.coeffs = ((a[0],b[0],c[0],d[0]),(a[1],b[1],c[1],d[1]))
        #Honestly I just don't even know anymore
        
        

    d!ef tan(self, t):
        
        q = self.a + self.b*t + self.c*t*t + self.d*t*t*t
        
        #return math.tan(q)
        return (0,0)

    
"""

