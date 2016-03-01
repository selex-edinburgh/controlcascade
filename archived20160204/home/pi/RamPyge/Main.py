import sys, time, threading
from Chariot import Chariot
from course import *
from Visualiser import Visualiser

### The main class. Put your control code here and start the chariot 
### by running this python script.
### <br />
### Put your instructions for controlling the chariot in the
### if __name__ == "__main__" condition block, after m.gui.start().
### If you remove m.gui.start(), the visualiser will not appear.<br>
### If you remove m=Main() or m.chariot.start(), the chariot will not 
### function.<br /><br />
### The code you should use should describe the goals of the chariot-
### for example, while there are more waypoints, traverse to the next,
### or for each waypoint, go to it:
### <br />
### <pre>for waypoint in m.arena.waypoints:<br /></pre>
### <pre>    m.chariot.goto(waypoint)</pre>
class Main:

    ### Initialises the chariot, arena and visualiser,
    ### and reads the configuration variables from the file
    ### into a dictionary.
    def __init__(self):
        cfg = self.getConfig()
        self.chariot = Chariot(cfg)
        self.arena = Assault()
        self.gui = threading.Thread(target=self.guiworker)
        #print(cfg)

    ### This function is the one taken as an argument to be the code
    ### run in the visualiser thread- basically creating an instance of
    ### Visualiser.
    def guiworker(self):
        # The visualiser needs to have access to the instances of
        # the chariot and the arena.
        self.v = Visualiser(self.chariot, self.arena)

    ### Loads variables from the configuration file (config.txt) into
    ### a dictionary. To access these: cfg['VAR_NAME']
    ### returns => configuration/environment variables (dict)
    def getConfig(self):
        cfg = {}
        with open('config.txt') as f:
            for line in f:
                if '=' in line:
                    tokens = line.replace((" "),"").replace("\n","").split('=')
                    cfg[tokens[0]] = [tokens[1]]
        return cfg


if __name__ == "__main__":
    m = Main()
    m.chariot.start()
    m.gui.start()

    ## Chariot control starts here
    for w in m.arena.waypoints:
        m.chariot.go(w,m.arena.obstacles)
    

