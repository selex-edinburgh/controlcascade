import sys, time, threading
from Chariot import Chariot
from course import *
from Visualiser import Visualiser

### The main class. Put your control code here and start the chariot 
### by running this python script. 
class Main:

    def __init__(self):
        self.chariot = Chariot()
        self.arena = Assault()
        self.gui = threading.Thread(target=self.guiworker)

    def guiworker(self):
        self.v = Visualiser(self.chariot, self.arena)


if __name__ == "__main__":
    m = Main()
    m.chariot.start()
    m.gui.start()

    m.chariot.go([],[(500,500)],0)
    
