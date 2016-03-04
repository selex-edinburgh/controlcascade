import time
import math
import threading
import sys
try:
    import smbus
except:
    print "I2C not connected"
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class OdoState(ObservableState):
    def __init__(self,mmPerPulse=0.1,rolloverRange=32768,rolloverCountL=0,rolloverCountR=0,initAngle=90):
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
        self.address = 4       	    # Seven bit Byte: as bit 8 is used for READ/WRITE designation.
        self.control = 176   	    # Tells sensor board slave to read odometers
        self.numbytes = 4      	
        self.timeStampFlow["sense"] = time.time()

def simUpdate(state,batchdata)    :
    odoControlUpdate(state, batchdata, False)
def realUpdate(state,batchdata)    :
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
        bus = smbus.SMBus(1)      
        RxBytes = bus.read_i2c_block_data(state.address, state.control, state.numbytes)
        
        leftReading = RxBytes[0]*256 + RxBytes[1] - 5000
        rightReading = RxBytes[2]*256 + RxBytes[3] - 5000
    state.timeStampFlow["sense"] = time.time()    
    """
    Applies rollover to the odometer readings,
    also checks for erraneous input from the sensors
    """
    state.totalPulseL = leftReading + state._rolloverCountL * state._rolloverRange
    state.totalPulseR = rightReading + state._rolloverCountR * state._rolloverRange
  
    if  (abs(state.totalPulseL - state.prevPulseL  ) > state._rolloverRange * 0.95):
        sign = math.copysign(1, state.totalPulseL - state.prevPulseL  )
        print "sign: ", sign
        state._rolloverCountL -= sign
        state.totalPulseL = leftReading + state._rolloverCountL * state._rolloverRange
        print "#################### rollover l", state.totalPulseL, state.prevPulseL   
        
    elif ((abs(state.totalPulseL - state.prevPulseL  ) > state._rolloverRange *  0.05) and           # check for erranous value from the odometers
        (abs(state.totalPulseL - state.prevPulseL  ) < state._rolloverRange *  0.95)):
        print "erraneous value"


    if ( abs(state.totalPulseR - state.prevPulseR  ) > state._rolloverRange * 0.95 ) :
        sign = math.copysign(1, state.totalPulseR - state.prevPulseR  )
        state._rolloverCountR -= sign
        state.totalPulseR = rightReading + state._rolloverCountR * state._rolloverRange
        print "#################### rollover r", state.totalPulseR, state.prevPulseR 
        
    elif ((abs(state.totalPulseR - state.prevPulseR  ) > state._rolloverRange *  0.05) and           # check for erranous value from the odometers
        (abs(state.totalPulseR - state.prevPulseR  ) < state._rolloverRange *  0.95)):
        print "erraneous value"
           

    state.prevDistTravel = state.distTravel
    state.distTravel +=  (( state.totalPulseL - state.prevPulseL ) + (state.totalPulseR -  state.prevPulseR )) / 2.0 * state._mmPerPulse
   

   
def odoToTrackTranslator( sourceState, destState, destQueue ):
    lrDifferenceMm = (sourceState.totalPulseL - sourceState.totalPulseR) * sourceState._mmPerPulse 
          
    angle =  (math.degrees(lrDifferenceMm / destState._trackWidth)   )+ sourceState._initAngle /4     
                
    destQueue.put({'messageType':'sense',
                   'sensedMove' :sourceState.distTravel - sourceState.prevDistTravel,
                   'sensedAngle':angle,
                   'timeStamp'  :sourceState.timeStampFlow["sense"]}) 
                   
