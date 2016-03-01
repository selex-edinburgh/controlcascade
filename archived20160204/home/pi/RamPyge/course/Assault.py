from Course import *

### An assault course as specified in the rules for Rampaging Chariots,
### Complete with obstacles, waypoints, etc.
class Assault(Course):

    ### Initialise assault course width, height, waypoints and obstacles.
    def __init__(self):
        self.width = 500
        self.height = 740

        ## Assault course -> 1 px : 10 mm
        mainw, mainh, loww, lowh, uph = [480, 730, 240, 250, 480]
        r1y , r2y, r3y = [60, 150, 240]
        lrbx = 128 # x of left pole row begin
        lrex = 220 # x of left pole row end
        rrbx = 270 # x of right pole row begin
        c1x, c2x, c3x = [lrbx, lrbx+20, lrbx+40]
        ldoorx = 20
        rdoorx = 4100
        doorw = 500
        seesawx = 215
        seesaww = 50

        
        self.waypoints = [(200,700)]
        self.obstacles = [Pole(c1x, r1y), Pole(c2x, r1y), Pole(c3x, r1y),\
                          Pole(c1x, r2y), Pole(c2x, r2y), Pole(c3x, r2y),\
                          Pole(c1x, r3y), Pole(c2x, r3y), Pole(c3x, r3y)]
        """self.walls = [Wall(0,0,480,00),Wall(480,0,0,0),Wall(480,480,480,0),\
                      Wall(360,480,480,480),Wall(360,730,360,480),\
                      Wall(128,730,360,730),Wall(128,480,128,730),\
                      Wall(0,480,128,480)]"""
        self.walls = []

        self.obstacles = super(Assault,self).readCsv()



                
    

        

        
