# -*- coding: utf-8 -*-
import time
import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class TrackState(ObservableState):
    def __init__(self, trackWidth, movementBudget):
        super(TrackState,self).__init__()
        #leg == line ending at next waypoint on route
        #self.legAngle  = 0.0
        self.noLegSet = True
        self.legCoeff  = (0.0,0.0,0.0)        
        self.legGoal = (0.0,0.0)     
        self.legOrigin = (0.0,0.0)
        self.currentAngle = 0
        self.currentPos = (1200.0,0,0)           
        self.demandAngle = 0
        self.demandPos = (0.0,0,0)            
        self._trackWidth = trackWidth       # 310.0 mm between wheels
        self._movementBudget = movementBudget       # 500.0 mm
        self.timeStamp = time.time()
        self.pole = (1200,0)
        self.timeStampFlow["control"] = time.time()
        self.timeStampFlow["sense"] = time.time()
        self.isCollision = False
        
        
def trackControlUpdate(state,batchdata):   
    for item in batchdata:      # Process items in batchdata
        """"
        Store timeStamp data
        """
        if 'timeStamp' not in item:
            pass
            #print "HERE ", item
        else:
            state.timeStampFlow[item['messageType']] = item['timeStamp']
            #print "TEST 3", item['timeStamp']
            #print "TEST 2", state.timeStampFlow
        if item['messageType'] == 'control':
 
            print "Old Leg goal ",  state.legGoal
            print "Current pos ", state.currentPos
            print "Demand pos", state.demandPos
            state.noLegSet = False
            state.legGoal = item['legGoal']
            state.legOrigin = item['legOrigin']    
            print 'track - control message'
            print "Leg goal ",  state.legGoal
    
        elif item['messageType'] == 'sense': ### integrate batch entries : sensedMove, sensedTurn
            #print 'track - sense message'
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
"""  
  deltaT = sourceState.timeStampFlow['control'] - time.time()
    
    message = {'messageType': 'time',
                'timeStamp':sourceState.timeStampFlow,
                'delta':delta_T,
                'sourceState': sourceState.__class__.__hash__}
           
    destQueue.put(message)
"""
    
    
    

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
    
    
    message = {'messageType':'control','demandTurn': turn * brakingPct / 100.0 ,
                                       'demandFwd' : move * brakingPct / 100.0,
                                       'timeStamp' : sourceState.timeStampFlow["control"]
                                       }
    destQueue.put(message)


def trackToScanSimTranslator(sourceState, destState, destQueue):
    message  =  {'messageType':'sense',
                'sensedPos': sourceState.currentPos,
                'sensedAngle':sourceState.currentAngle}
    destQueue.put(message)
    
def trackToVisualTranslator(sourceState, destState, destQueue):
    message = {'messageType':'robot',
    'robotPos':sourceState.currentPos,
    'robotAngle':sourceState.currentAngle,
    'goal':sourceState.legGoal,
    'demandPos':sourceState.demandPos}
    destQueue.put(message)



def angleDiff ( fromAngle, toAngle ) :
    angleDiff = toAngle - fromAngle
    if angleDiff > 180:
        angleDiff -= 360
    elif angleDiff < -180:
        angleDiff += 360
    return angleDiff


      
    
