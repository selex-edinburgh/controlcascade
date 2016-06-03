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
    destQueue.put({'messageType':'sense',
               'scanRange':self.scanRange,
               'scanAngle':self.scanAngle  })
