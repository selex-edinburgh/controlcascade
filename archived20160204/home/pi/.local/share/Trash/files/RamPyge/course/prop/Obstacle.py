
import math

class Obstacle:

    FOV = 26.6
    description = "obstacle"

    def __init__(self, args):
        self.a0, self.a1, self.d0, self.d1 = args
        self.dT = (self.d0+self.d1)/2
        self.awidth = self.a0 - self.a1
        self.aT = self.a1 + self.awidth/2
        self.width = (2*d0)*math.tan(math.radians((self.awidth-self.FOV)/2))


    

    
