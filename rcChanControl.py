'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
# -*- coding: utf-8 -*-
import time
import math
import os
import threading
try:
    import serial
except:
    print "Serial not connected.."
from plumbing.observablestate import ObservableState
from plumbing.arcnode import ArcNodeObserverTranslator

'''
    Uncomment this section and motorCommand file open part further down to
    get back motor date to put in Graphs
'''
##try:        # delete log file
##    os.rename('motorCommands.txt','log/%s.old' % time.time())
##    os.remove('motorCommands.txt')
##except OSError:
##    print "os fail"

class RcChanState(ObservableState):
    def __init__(self, lrChange, fwdbkChange, minSpeedFwdBk, minSpeedLR, maxSpeedFwdBk, maxSpeedLR, speedScalingFwdBk, speedScalingLR, turnOffset = 0, turnBiasLOverR = 1.0):
        super(RcChanState,self).__init__()
        self._nullFwd = 127
        self._nullTurn = 127
        self._turnBiasLOverR = turnBiasLOverR
        self._maxDemand = 127
        self.currentTurn = self._nullTurn
        self.currentFwd = self._nullFwd
        self.demandTurn = self._nullTurn
        self.demandFwd = self._nullFwd
        self.minSpeedFwdBk = minSpeedFwdBk  
        self.minSpeedLR = minSpeedLR        
        self.maxSpeedFwdBk = maxSpeedFwdBk  
        self.maxSpeedLR = maxSpeedLR
        self.startHdgToggle = True
        self.startHdg = 0
        self.hdg2Go = 0                     #how much the RC has to turn its heading so that it is facing the next waypoint
        self.dist2Go = 0                    #how much distance the RC would need to cover to reach the next waypoint if it drove straight towards it
        self.driveMode = None               #says if the RC is turn left, right, moving fwd or stationary
        self.accelLat = 1.5                 #rate of lateral acceleration (default 1.5)
        self.decelLat = 0.5                 #rate of lateral deceleration (default 0.5)
        self.accelLong = 0.5                #rate of longitudinal acceleration (default 0.5)
        self.decelLong = 0.1                #rate of longitudinal deceleration (default 0.1)
        self.turnPower = 0                  #the amount to add to nullTurn which turns you in which direction 
        self.fwdPower = 0                   #the amount to add to nullFwd which drives you fwd, might take into account backwards in future
        
        self.speedScalingFwdBk = speedScalingFwdBk
        self.speedScalingLR = speedScalingLR
        self._lrChange = lrChange * speedScalingLR
        self._fwdbkChange = fwdbkChange * speedScalingFwdBk
        self.timeStamp    = time.time()

        self.minSpeedMotorL = 40
        self.minSpeedMotorR = 40
        self.nullMotorL = 254
        self.nullMotorR = 0

        self.timeStampFlow["control"] = time.time()
        try:
            self.ser= serial.Serial(            #Set up Serial Interface
            port="/dev/ttyS0",                #UART using Tx pin 8, Rx pin 10, Gnd pin 6
            baudrate=38400,                      #bits/sec
            bytesize=8, parity='N', stopbits=1, #8-N-1  protocol
            timeout=1                           #1 sec
            )
        except:
            print "Serial not connected..."

def clip(x):
    return min(254,max(1,x))

def simMotor(state, batchdata):
    rcChanControlUpdate(state, batchdata, False)

def realMotor(state, batchdata):
    rcChanControlUpdate(state, batchdata, True)

def rcChanControlUpdate(state,batchdata, motorOutput):
    for item in batchdata:      # process items in batchdata

        if 'timeStamp' in item:
            state.timeStampFlow[item['messageType']] = item['timeStamp']
            pass

        if item['messageType'] == 'control':
##                state.demandTurn = clip(item['demandTurn'] * state.speedScalingLR * state._maxDemand + state._nullTurn)   ## expects anti clockwise
##                state.demandFwd  = clip(item['demandFwd'] * state.speedScalingFwdBk * state._maxDemand + state._nullFwd)   ## inserted minus
##                state.demandTurn = state.demandTurn * state._turnBiasLOverR if state.demandTurn > 0.0 else state.demandTurn / state._turnBiasLOverR
            state.hdg2Go = item['hdg2Go']
            state.dist2Go = item['dist2Go']
            state.driveMode = item['driveMode']
        elif item['messageType'] == 'sense':
            pass

    if not batchdata:       # if no messages (loops stopped) set the speed to stationary
        state.demandTurn = state._nullTurn
        state.demandFwd = state._nullFwd


##    state.currentTurn = clip(limitedChange(state.currentTurn, state.demandTurn , state._lrChange)) 
##    state.currentFwd = clip(limitedChange(state.currentFwd, state.demandFwd , state._fwdbkChange))

    #reset for start dist and hdg for the motor rate calculations
    if state.driveMode != 'TurnR' and state.driveMode != 'TurnL':
        state.startHdgToggle = True
    elif state.startHdgToggle == True:
        state.startHdg2Go = hdg2Go
        state.startHdgToggle = False
    if state.driveMode != 'MoveFwd':
        state.startDistToggle = True
    elif state.startDistToggle == True:
        state.startDist2Go = dist2Go
        state.startDistToggle = False

    #calculates the rate at which the motor power is increased or decreased, with proportion of dist & hdg to go    
    accelRateR = ((state.startHdg2Go - state.hdg2Go)*state.accelLat)+state.minSpeedLR
    decelRateR = (state.hdg2Go*state.decelLat)+(state.minSpeedLR/2)
    accelRateL = ((state.startHdg2Go - state.hdg2Go)*state.accelLat)-state.minSpeedLR
    decelRateL = (state.hdg2Go*state.decelLat)-(state.minSpeedLR/2)
    accelRateFwd = ((state.startDist2Go - state.dist2Go)*state.accelLong)+state.minSpeedFwdBk
    decelRateFwd = (state.dist2Go*state.decelLong)+(state.minSpeedFwdBk/2)

    #controls if accelerating, cruising or decelerating after being given a driveMode
    if state.driveMode == 'TurnR':
        #turn right
        if decelRateR < maxSpeedLR:
            #decel to minSpeed
            turnPower = minSpeedLR if decelRateR < minSpeedLR else decelRateR
            fwdPower = 0
        else:
            #accel to maxSpeed
            turnPower = maxSpeedLR if accelRateR > maxSpeedLR else accelRateR
            fwdPower = 0
    elif state.driveMode == 'TurnL':
        #turn left
        if decelRateL > -maxSpeedLR:
            #decel to minSpeed
            turnPower = -minSpeedLR if decelRateL > -minSpeedLR else decelRateL
            fwdPower = 0
        else:
            #accel to maxSpeed
            turnPower = -maxSpeedLR if accelRateR < -maxSpeedLR else accelRateR
            fwdPower = 0
    elif state.driveMode == 'MoveFwd':
        #move forward
        if decelRateFwdBk < maxSpeedFwdBk
            #decel to minSpeed
            turnPower = 0
            fwdPower = minSpeedFwdBk if decelRateFwd < minSpeedFwdBk else decelRateFwd
        else:
            #accel to maxSpeed
            turnPower = 0
            fwdPower = maxSpeedFwdBk if accelRateFwd > maxSpeedFwdBk else accelRateFwd
    elif state.driveMode == 'Parked':
        #stationary
        turnPower = 0
        fwdPower = 0

    state.currentTurn = state._nullTurn + turnPower
    state.currentFwd = state._nullFwd + fwdPower

##    motorL = state.currentFwd + state.currentTurn
##    motorR = state.currentFwd - state.currentTurn
##    if motorL > state.nullMotorL and motorL < state.nullMotorL + State.minSpeedMotorL:
##        motorL = state.nullMotorL + State.minSpeedMotorL
##    elif motorL < state.nullMotorL and motorL > state.nullMotorL - State.minSpeedMotorL:
##        motorL = state.nullMotorL - State.minSpeedMotorL
##    if motorR > state.nullMotorR and motorR < state.nullMotorR + State.minSpeedMotorR:
##        motorR = state.nullMotorR + State.minSpeedMotorR
##    elif motorR < state.nullMotorR and motorR > state.nullMotorR - State.minSpeedMotorR:
##        motorR = state.nullMotorR - State.minSpeedMotorR
##    state.currentFwd = (motorL + motorR)/2
##    state.currentTurn = (motorL - motorR)/2
    
##    f = open('motorCommands.txt', 'a')
##    print >> f, time.time(), ",", int(state.currentFwd), ",", int(state.currentTurn)
##    f.close()
    
    if motorOutput:
        state.ser.write(chr(clip(int(state.currentFwd))))       #Output to Motor Drive Board
        state.ser.write(chr(clip(int(state.currentTurn))))      #Output to Motor Drive Board
        
##    if time.time() - int(time.time()) < 0.05: print state.currentFwd, state.currentTurn#, state.demandFwd, state.demandTurn
        
def limitedChange(startX, endX, magnitudeLimit):
    diff = endX - startX
    if diff == 0: return startX
    diffSign = math.copysign(1,diff)
    change = diffSign * ( min(abs(diff),magnitudeLimit) )
    return startX + change

def rcChanToVsimTranslator( sourceState, destState, destQueue ):
    destQueue.put({'messageType':'control',
                   'rcTurn' :-(sourceState.currentTurn/sourceState._maxDemand - 1.0),
                   'rcFwd'  :sourceState.currentFwd/sourceState._maxDemand - 1.0 ,
                   'timeStamp' : sourceState.timeStampFlow})
