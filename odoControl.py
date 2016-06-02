import time
import math
import threading
import sys

from subprocess import call
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class OdoState(ObservableState):
    def __init__(self,mmPerPulse=0.1,rolloverRange=32768,rolloverCountL=0,rolloverCountR=0,initAngle=90, odoFilename="fifo.tmp", odoReadRate=16000):
        super(OdoState,self).__init__()
        self.totalPulseL = 0
        self.totalPulseR = 0
        self.prevPulseL = 0
        self.prevPulseR = 0
        self.prevDistTravel = 0
        self.distTravel = 0
        self._initAngle = initAngle
        self._mmPerPulse = mmPerPulse       # 1
        self._rolloverRange = rolloverRange         # 32768
        self._rolloverCountL = rolloverCountL       # 0
        self._rolloverCountR = rolloverCountR        # 0
        self._odoFilename = odoFilename         # "fifo.tmp"
        self._odoReadRate = odoReadRate
        self.lr = 0
        self.rr = 0
        self.timeStampFlow["sense"] = time.time()
        self.realMode = False
        call(["./fifo",self.odoReadRate,self.odoFilename]) #Run the C exe - Odometer Reader

def simUpdate(state,batchdata):
    odoControlUpdate(state, batchdata, False)
    
def realUpdate(state,batchdata):
    odoControlUpdate(state, batchdata, True )

def odoControlUpdate(state,batchdata, doRead):
    state.prevPulseL = state.totalPulseL
    state.prevPulseR = state.totalPulseR

    for item in batchdata:          # process items in batchdata
        if item['messageType'] == 'control':
            pass
        elif item['messageType'] == 'sense':
            leftReading = item['pulseL']
            rightReading = item['pulseR']

    if len(batchdata)==0 : return
   
    if doRead :     # read items from the i2c interface
        state.realMode = True # so visualiser knows real chariot is running      

        #RxBytes = state.bus.read_i2c_block_data(state.address, state.control, state.numbytes) # tell the sensor board to read the odometers
        
        leftReading = 
        rightReading = 
        
    try:
        state.timeStampFlow["sense"] = time.time()    
        
        state.totalPulseL = leftReading     
        state.totalPulseR = rightReading

        state.prevDistTravel = state.distTravel
        state.distTravel +=  (( state.totalPulseL - state.prevPulseL ) + \
                                (state.totalPulseR -  state.prevPulseR )) / 2.0 * state._mmPerPulse
    except:
        pass
        
def odoToTrackTranslator( sourceState, destState, destQueue ):
    lrDifferenceMm = (sourceState.totalPulseL - sourceState.totalPulseR) * sourceState._mmPerPulse 
          
    angle =  (math.degrees(lrDifferenceMm / destState._trackWidth) %360   )+ sourceState._initAngle      # correct (y) **depends on if trackwidth is correct**
                
    destQueue.put({'messageType':'sense',
                   'sensedMove' :sourceState.distTravel - sourceState.prevDistTravel,
                   'sensedAngle':angle,
                   'timeStamp'  :sourceState.timeStampFlow["sense"]}) 

def odoToVisualTranslator(sourceState, destState, destQueue):
    destQueue.put({'messageType':'odo',
                    'leftReading': sourceState.totalPulseL,
                    'rightReading': sourceState.totalPulseR,
                    'mode': sourceState.realMode})
