import time
import math
import threading
import sys
import subprocess as sub

from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class OdoState(ObservableState):
    def __init__(self,mmPerPulse=0.1,initAngle=90, driver="./fifo", odoPipename="fifo.tmp", odoReadRate="16000"):
        super(OdoState,self).__init__()
        self.totalPulseL = 0
        self.totalPulseR = 0
        self.prevPulseL = 0
        self.prevPulseR = 0
        self.prevDistTravel = 0
        self.distTravel = 0
        self._initAngle = initAngle         # 0
        self._mmPerPulse = mmPerPulse       # 1
        self._driver = driver               # "./fifo"
        self._odoPipename = odoPipename     # "fifo.tmp"
        self._odoReadRate = odoReadRate     # 16000
        self.timeStampFlow["sense"] = time.time()
        self.realMode = False
        cmd = ['sudo', 'chrt', '-f', '98', self._driver,self._odoReadRate,self._odoPipename] # sudo chrt -f 98 ./fifo 16000 fifo.tmp
        try: 
            sub.Popen(cmd, shell=True, stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE) #Run the C exe - Odometer Reader
        except Exception as err:
            print err.errno
            print err.strerr
        self.generator = generatorFunction(self._odoPipename)
def simUpdate(state,batchdata):
    odoControlUpdate(state, batchdata, False)
    
def realUpdate(state,batchdata):
    odoControlUpdate(state, batchdata, True )
    
def generatorFunction(pipename): 
    isOpen = False
    previousJ = (0,0)
    while True:
        if(isOpen):
            try:
	    	j = f.readline()
            	j = j.strip().split(",")
            	yield (int(j[0]),int(j[1]))
		previousJ = j
	    except:
		yield previousJ 	
        else:    
            try:
                f = open(pipename, 'r')
                isOpen = True
            except IOError as err:
                isOpen = False
                print err.errno
                print err.strerror
                yield previousJ

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
        readings = state.generator.next()
        leftReading = readings[0]
        rightReading = readings[1]
        
        
    try:
        state.timeStampFlow["sense"] = time.time()    
        
        state.totalPulseL = leftReading     
        state.totalPulseR = rightReading
        print state.totalPulseL, state.totalPulseR
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
