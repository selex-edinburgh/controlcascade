'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
# -*- coding: utf-8 -*-
import time
import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class TrackState(ObservableState):
    def __init__(self, trackWidth, movementBudget):
        super(TrackState,self).__init__()

        self.noLegSet = True
        self.legCoeff  = (0.0,0.0,0.0)        
        self.legGoal = (0.0,0.0)     
        self.legOrigin = (0.0,0.0)
        self.currentAngle = 0
        self.currentPos = (2390.0,4630.0,0)           
        self.demandAngle = 0
        self.demandPos = (0.0,0,0)            
        self._trackWidth = trackWidth       # 310.0 mm between wheels
        self._movementBudget = movementBudget       # 500.0 mm
        self.timeStamp = time.time()
        self.pole = (1200,0)
        self.timeStampFlow["control"] = time.time()
        self.timeStampFlow["sense"] = time.time()
        self.isCollision = False
        self.nearWaypoint = False       # check is near next waypoint
        
def trackControlUpdate(state,batchdata):   
    for item in batchdata:      # Process items in batchdata
        if 'timeStamp' not in item:
            pass
            
        else:
            state.timeStampFlow[item['messageType']] = item['timeStamp']
            
        if item['messageType'] == 'control':
            state.noLegSet = False
            state.legGoal = item['legGoal']
            state.legOrigin = item['legOrigin']  
            state.nearWaypoint = item['nearWaypoint']            
    
        elif item['messageType'] == 'sense': ### integrate batch entries : sensedMove, sensedTurn
            #approximate as movement along circular arc, effective direction being mid-way on arc
            
            halfArcTurn = (item['sensedAngle']-state.currentAngle) / 2.0
            halfArcMove = (item['sensedMove']) / 2.0
            
            if math.radians(halfArcTurn) < 0.1:  # small angle approximation sin(angle) = angle : and avoid divide-by-zero risk
                linearMove = abs(2.0 * halfArcMove )
            else:
                linearMove = abs(2.0 * math.sin(math.radians(halfArcTurn) ) * halfArcMove / math.radians(halfArcTurn)) # linear move is shorter than arc
        
            midwayAngle = state.currentAngle + halfArcTurn
            state.currentPos = (state.currentPos[0] + linearMove * math.sin(math.radians(midwayAngle)), # x move along effective direction
                                    state.currentPos[1] + linearMove * math.cos(math.radians(midwayAngle))) # y move along effective direction
                    
            state.currentAngle = item['sensedAngle']       
            state.timeStamp = time.time()
             
       # elif item['messageType'] == 'obstacle':
        #    state.isCollision = item['collision']
         #   print item['collision']
           # if((state.legGoal[0] - state.legOrigin[0]) * (state.pole[1] - state.legOrigin[1]) == \
           # (state.pole[0] - state.legOrigin[0]) * (state.legGoal[1] - state.legOrigin[1])):
           #     print "OMG GONNA COLLIDE"
           
    if len(batchdata) == 0: return      # do nothing here, unless new control or sense messages have arrived
    
    if state.isCollision == True:       # collison warning 
        state.demandPos = (state.currentPos[0] - 100, state.currentPos[1])
        print "Collision"
        return 

    #Run update of control laws
    # http://mathworld.wolfram.com/Point-LineDistance2-Dimensional.html
    # angle = math.atan2( (nextWP[1]-prevWP[1]),(nextWP[0]-prevWP[0] ) )
    # line  : ax + by + c = 0
    # coefficients
    # a=(yB−yA) , b=(xA−xB) and c=(xByA - xAyB)
    a = state.legGoal[1] - state.legOrigin[1] 
    b = state.legOrigin[0] - state.legGoal[0]
    c = (state.legGoal[0] * state.legOrigin[1]) - (state.legOrigin[0] * state.legGoal[1])
    abDist = math.hypot(a,b)
    state.demandPos = state.legGoal
    if abDist < 1e-10 or state.currentPos == state.legGoal: return #avoid divide by zero
    distToLeg = (a*state.currentPos[0] + b*state.currentPos[1] + c ) / abDist
    # along perpendicular vector ( a , b )
    deltaXfromLeg = a * distToLeg / abDist
    deltaYfromLeg = b * distToLeg / abDist
    closePointOnLeg =  (state.currentPos[0] - deltaXfromLeg, state.currentPos[1] -  deltaYfromLeg)
    distToGoal = math.hypot( state.legGoal[0] - closePointOnLeg[0], state.legGoal[1] - closePointOnLeg[1] )
    absToLeg =  abs(distToLeg)
    moveAmount = distToGoal 
    if absToLeg > distToGoal: moveAmount =  0
    #print "absToLeg", absToLeg, "dist: ", distToGoal
    # demandPos is a point on the Leg, maxMove along from closePointOnLeg
    state.demandPos = ( (state.legGoal[0] - closePointOnLeg[0]) / distToGoal * moveAmount + closePointOnLeg[0] , \
                    (state.legGoal[1] - closePointOnLeg[1]) / distToGoal * moveAmount + closePointOnLeg[1])

    #state.demandAngle = math.degrees(math.atan2( state.demandPos[1] -  state.currentPos[1] , state.demandPos[0] - state.currentPos[0] ))
    state.demandAngle = math.degrees(math.atan2( state.demandPos[0] -  state.currentPos[0] , state.demandPos[1] - state.currentPos[1] ))
    
    #print "demand pos", state.demandPos
    
    state.timeStampFlow["control"] = state.timeStampFlow["sense"]
    
def trackToStatsTranslator(sourceState, destState, destQueue):
    #print sourceState.timeStampFlow
    pass

def trackToRouteTranslator( sourceState, destState, destQueue ):
    message = {'messageType':'sense','sensedPos':sourceState.currentPos}
    destQueue.put(message)

def trackToRcChanTranslator( sourceState, destState, destQueue ):
    dtgFactor = math.hypot(sourceState.demandPos[0]-sourceState.currentPos[0],
                      sourceState.demandPos[1]-sourceState.currentPos[1] ) / 4.0#TODO
    brakingPct = round(min(100.0, dtgFactor)  ,0)
    if brakingPct < 15.0 : brakingPct = 0
    turn = angleDiff(sourceState.currentAngle, sourceState.demandAngle) / 90
    move = max ( 1 - abs(turn), 0 )
    print -turn * 127 + 127
    print move * 127 + 127
    message = {'messageType':'control','demandTurn': turn * brakingPct / 100.0 ,
                                       'demandFwd' : move * brakingPct / 100.0,
                                       'timeStamp' : sourceState.timeStampFlow["control"]
                                       }
    destQueue.put(message)

def trackToScanSimTranslator(sourceState, destState, destQueue):
    destQueue.put({'messageType':'sense',
                'sensedPos': sourceState.currentPos,
                'sensedAngle':sourceState.currentAngle})
    
def trackToVisualTranslator(sourceState, destState, destQueue):
    destQueue.put({'messageType':'robot',
    'robotPos':sourceState.currentPos,
    'robotAngle':sourceState.currentAngle,
    'goal':sourceState.legGoal,
    'demandPos':sourceState.demandPos,
    'nearWaypoint':sourceState.nearWaypoint})

def angleDiff ( fromAngle, toAngle ) :
    angleDiff = toAngle - fromAngle
    if angleDiff > 180:
        angleDiff -= 360
    elif angleDiff < -180:
        angleDiff += 360
    return angleDiff


      
    
