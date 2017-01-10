'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import time
import math
import threading
import sys

# Set up GPIO pins
try:
    import RPi.GPIO as GPIO
    GPIO_Present = True
except ImportError as err: # catch the RunTimeError and output a response
    GPIO_Present= False
    print err
    print ("Error: Can't import RPi.GPIO")

from plumbing.observablestate import ObservableState
from plumbing.arcnode import ArcNodeObserverTranslator

class OdoState(ObservableState):
    def __init__(self,wheelDiaRt=150.0, wheelDiaLt=150.0,initAngle=0):
        super(OdoState,self).__init__()
        self.totalPulseL = 0
        self.totalPulseR = 0
        self.prevPulseL = 0
        self.prevPulseR = 0
        self.offsetL = 0
        self.offsetR = 0
        self._rolloverRange = 1024.0
        self.prevDistTravel = 0
        self.distTravel = 0
        self._initAngle = initAngle
        self._mmPerPulseRt = wheelDiaRt * math.pi/1024.0
        self._mmPerPulseLt = wheelDiaLt * math.pi/1024.0
        
        self.timeStampFlow["sense"] = time.time()
        self.realMode = False
        self.firstTime = True
        if GPIO_Present:
            #Initialise GPIO
            GPIO.setwarnings(False)
            GPIO.cleanup()
            GPIO.setmode(GPIO.BCM)      #GPIO number designation (not pin nos)
            GPIO.setup(18, GPIO.IN)     #Data pin left Odometer
            GPIO.setup(22, GPIO.IN)     #Data pin Right Odometer
            GPIO.setup(24, GPIO.OUT)    #Chip Select
            GPIO.setup(23, GPIO.OUT)    #Clock pin comm

'''
   The read_odometers function will read angle and status data from the two
   odometers directly and pass the result back to the odoControlUpdate().
 
   The Odometers use a simple synchronised two way data link.
   The GPIO Chip Select pins on both odometers are connected together
   so that both odometers are triggered to start simultaneously.
   The GPIO Clock pins on both odometers are also connected together
   so that the 16 data bits are clocked out simultaneously.
   The Odometer Data output pins are connected to separate GPIO pins
   and the bit values are read separately.
   We assemble these individual bits of data into separate 16 bit words.
   Each 360 degree rotation of the wheel is divided up into 1024 steps.
   During every rotation the data counts from 0 to 1024 and then starts again.
   The step change between 0 and 1024 and visa versa is called a rollover
'''
def read_Odometers():
    
    # initialise local variables
    TICK = 0.000005     #Half Odom Serial clock period 5us=100K bits/s(Max 1MHz)
    i = 15              #bit count index number
    readBitLt = 0       #Lt Odom Data bit
    readBitRt = 0       #Rt Odom Data bit
    angDataLt = 0       #Lt Odom angular data in 10 bit word
    angDataRt = 0       #Rt Odom angular data in 10 bit word
    statusLt = 0        #Lt Odom status in 6 bit word
    statusRt = 0        #Rt Odom status in 6 bit word   

    # Read the Odometers
    # Bring the chip select pin high and then low before reading data.
    GPIO.output(24, True)   #Chip Select pin High (normal state)
    time.sleep(TICK)        #Half odom Serial clock period
    GPIO.output(23, True)   #Clock pin High (normal state)
    time.sleep(TICK)
    GPIO.output(24, False)  #Chip Select pin Low (both odom triggered to output data)
    time.sleep(TICK)        #Wait min of 500ns
    
    # bit data changes on each rising edge of clock 
    while i >= 0:   # loop 16 times to read 16 bits of data from the odometers
                    # the most significant bit (msb) is first (bit 15) 
                    # the least significant bit (lsb) is last (bit 0)   
        # pulse the clock pin Low and High and then read the two data pins
        GPIO.output(23, False)  #Clock pin Low
        time.sleep(TICK)
        GPIO.output(23, True)   #Clock pin High 
        time.sleep(TICK)        #Wait half clock period and then read bit data        
        readBitLt = GPIO.input(18)    #read a bit from Lt odometer Data pin
        readBitRt = GPIO.input(22)    #read a bit from Rt odometer Data pin

        # shift each bit left to form two 10 bit binary words for angle data
        # and two 5 bit binary words for odometer chip and magnet status 
        #The first bit received is the most significant bit (msb bit 15)
        if i > 5:  #first 10 bits contain angular rotation data (0 to 1024)
            angDataLt =((angDataLt << 1) + readBitLt)   #bits 15 to 6
            angDataRt =((angDataRt << 1) + readBitRt) 
        else:      #last 6 bits contain odometer status data for analysis
            statusLt = ((statusLt << 1) + readBitLt)    #bits 5 to 0
            statusRt = ((statusRt << 1) + readBitLt)

        i -= 1      #decrement bit count index number

    time.sleep(TICK)        #Complete clock cycle
    GPIO.output(24, True)   #Chip Select pin High (back to normal state)
    return (angDataLt, angDataRt, statusLt, statusRt)   #return values to main()

'''
    The read_correct_odo function corrects 
'''
def read_correct_odo():
    (angDataLt,angDataRt, statusLt,statusRt) = read_Odometers()
    return (angDataLt,1024-angDataRt, statusLt,statusRt)

'''    
    The handle_rollovers function will detect any rollovers that may
    occur during runtime and thereby achieve a continuous distance count
    A rollover is a jump in angDataLt or angDataRt between 0 and 1024
    One wheel rotation is divided into 3 equal sectors (1024/3 = 341 bits)
    if the new angle & the previous angles are in sectors adjacent to the jump
    a rollover has occurred and 1024 is added or subtracted from odom distance
    Note: Time interval between odometer reads must be less than time taken
    for wheel to rotate 2/3 of turn (this determines max wheel speed allowed)
    This function is called from odoControlUpdate().
'''
def handle_rollovers(angDataLt,angDataRt,prevAngDataLt,prevAngDataRt,\
    odomDistLt,odomDistRt):
    # Calculate change in odometer angles
    changeLt = angDataLt - prevAngDataLt  #change in dataLt since last reading
    changeRt = angDataRt - prevAngDataRt  #change in dataRt since last reading

    if (angDataLt <341) and (prevAngDataLt >683):  #adjacent rollover sectors
        odomDistLt = odomDistLt + 1024 + changeLt  #positive rollover
    elif (angDataLt >683) and (prevAngDataLt <341):#adjacent rollover sectors
        odomDistLt = odomDistLt - 1024 + changeLt  #negative rollover 
    else:
        odomDistLt = odomDistLt + changeLt         #no rollover 

    if (angDataRt <341) and (prevAngDataRt >683):  #adjacent rollover sectors
        odomDistRt = odomDistRt + 1024 + changeRt  #positive rollover
    elif (angDataRt >683) and (prevAngDataRt <341):#adjacent rollover sectors
        odomDistRt = odomDistRt - 1024 + changeRt  #negative rollover
    else:
        odomDistRt = odomDistRt + changeRt         #no rollover
    
    prevAngDataLt = angDataLt     #load new dataLt into prevDataLt for next loop
    prevAngDataRt = angDataRt     #load new dataRt into prevDataRt for next loop
            
    return(odomDistLt,odomDistRt,prevAngDataLt,prevAngDataRt)

def simUpdate(state,batchdata)    :
    odoControlUpdate(state, batchdata, False)
    
def realUpdate(state,batchdata)    :
    odoControlUpdate(state, batchdata, GPIO_Present )

def odoControlUpdate(state,batchdata, doRead):
    state.prevPulseL = state.totalPulseL
    state.prevPulseR = state.totalPulseR

    simDataAvailable = False
    for item in batchdata:          # process items in batchdata
        if item['messageType'] == 'control':
            pass
        elif item['messageType'] == 'sense':
            angDataLt = item['pulseL']  #from simulation
            angDataRt = item['pulseR'] #from simulation
            simDataAvailable = True

    
    if not doRead: #simulated or no odometers available
        # angDataLt and angDataRt are assigned to the latest values from batchdata above
        state.realMode = False
        if not simDataAvailable : return # no data to assign from -> return
    else :  # doRead == true   # read items from GPIO Pins
        state.realMode = True # so visualiser knows real chariot is running

        # read odometers for raw angle data and status then correct right odometer
        (angDataLt,angDataRt,statusLt,statusRt) = read_correct_odo()

    state.timeStampFlow["sense"] = time.time() #Keeping track of latency to be passed to stats loop

    if state.firstTime == True:         #First time setup for prevAngData
        state.offsetL = angDataLt       #sets left offset for correction can be made on later values to centre to 0
        state.offsetR = angDataRt       #sets right offset for correction can be made on later values to centre to 0
        state.firstTime = False

    # calculate odometer distances by actioning rollovers
    (state.totalPulseL,state.totalPulseR,state.offsetL,state.offsetR)= handle_rollovers\
        (angDataLt,angDataRt,state.offsetL,state.offsetR,\
         state.totalPulseL,state.totalPulseR)

    #intergrating pulse L and R to get a total distance travelled
    state.prevDistTravel = state.distTravel
    state.distTravel +=  (( state.totalPulseL - state.prevPulseL ) * state._mmPerPulseLt + \
                            (state.totalPulseR -  state.prevPulseR )* state._mmPerPulseRt) / 2.0

def odoToTrackTranslator( sourceState, destState, destQueue ):
    lrDifferenceMm = (sourceState.totalPulseL * sourceState._mmPerPulseLt) - (sourceState.totalPulseR * sourceState._mmPerPulseRt)

    angleRadians = (lrDifferenceMm/destState.turnRadius)*destState.turnFactor * destState.underTurnFudge# 0.63 fudge! to make full turn happen
      # calculates the relative heading and applies the turnFactor
    
    angle =  (math.degrees(angleRadians)+ sourceState._initAngle)%360   # applies offset to apply absolute heading
                
    destQueue.put({'messageType':'sense',
                   'sensedMove' :sourceState.distTravel - sourceState.prevDistTravel,
                   'sensedAngle':angle,
                   'timeStamp'  :sourceState.timeStampFlow["sense"]}) 

def odoToVisualTranslator(sourceState, destState, destQueue):
    destQueue.put({'messageType':'odo',
                    'leftReading': sourceState.totalPulseL,
                    'rightReading': sourceState.totalPulseR,
                    'mode': sourceState.realMode})

##stateObj = OdoState(150.0 * math.pi/1024.0,90.0)
##print stateObj.__dict__
##while True:
##    realUpdate(stateObj,[])
##    time.sleep(0.2)
##    print stateObj.totalPulseL, stateObj.totalPulseR, stateObj.prevPulseL, stateObj.prevPulseR, stateObj.distTravel
##    
    
    

