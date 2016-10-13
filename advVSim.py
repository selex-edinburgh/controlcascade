'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import time
import math
import i2c
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator


class advVSimState(observablestate):
    def __init__(self, cfg):
        super(advVSimState, self).__init__()
        self.scanRange = 0.0 #mm
        self.scanAngle = 0.0 #relative to the direction of the chariot
        
        self.cfg = cfg
        self.connect = False
        if 'US_RANGER_ADDRESS' in self.cfg:
            self.connect = True
        else:
            print "WARNING: No rangefinder connected!"       #busnum = 1 if self.getPiRevision() > 1 else 0
        self.bus = i2c(self.cfg['US_RANGER_ADDRESS'])
    
    def read(self):
        self.bus.write8(self.cfg['US_REQUEST'], self.cfg['US_RANGE'])
        time.sleep(0.005)
        results = self.bus.readList(self.cfg['US_RANGE'],2) #Ranger output is composed of 2 bytes
        if results is not None:  
            result = (results[0] << 8) | results[1]
            return result/58 # Distance in mm
        else:
            return -1
        

def advVSimControlUpdate(state, batchdata):

    for item in batchdata:
        if item['messageType'] == 'control':
            pass
        elif item['messageType'] == 'sense':
            pass
            
def advVSimToSensorTranlsator(sourceState, destState, destQueue):
    message = {'messageType':'sense',
               'scanRange':self.scanRange,
               'scanAngle':self.scanAngle  }
    destQueue.put(message)