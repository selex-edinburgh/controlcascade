import Course
from prop import *

### An assault course as specified in the rules for Rampaging Chariots,
### Complete with obstacles, waypoints, etc.
class Assault(Course.Course):

    ### Initialise assault course width, height, waypoints and obstacles.
    def __init__(self):
        self.width = 800
        self.height = 750
        self.waypoints = []
        self.obstacles = []
        self.walls = [Wall(0,0,480,00),Wall(480,0,0,0),Wall(480,480,480,0),\
                      Wall(360,480,480,480),Wall(360,730,360,480),\
                      Wall(128,730,360,730),Wall(128,480,128,730),\
                      Wall(0,480,128,480)]

        

        
