# -*- coding: utf-8 -*-
import time
import math
import threading

from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator
from waypoint import *

class TrackState(ObservableState):
    def __init__(self, wheelBase, trackWidth, movementBudget):
        super(TrackState,self).__init__()

        self.noLegSet = True
        self.legCoeff  = (0.0,0.0,0.0)
        self.legGoal = WaypointManager.createWaypoint(0.0,0.0)
        self.legOrigin = WaypointManager.createWaypoint(0.0,0.0)
        self.currentAngle = 0
        #self.currentPos = (2390.0,4630.0) # Uncomment this line to have RC draw at centre of screen
        self.currentPos = (-500.0,-500.0)  # This draws the RC off screen before clicking Start
        self.demandAngle = 0
        self.demandPos = (0.0,0.0)
        self._trackWidth = trackWidth                   # nominal 237.0 mm between wheels l/r
        self._wheelBase = wheelBase                     # nominal 200.0 mm between wheels f/b
        self.turnRadius = math.hypot(self._trackWidth, self._wheelBase)/2.0 # value should be around 155.0 mm
        self.turnFactor = ((self._trackWidth/2.0)/self.turnRadius)**2.0 # takes into account the turning component
        # and the turn radius to create a correction value that can be applied to the heading (0.58)
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
            state.legGoal = item['legGoal']
            state.legOrigin = item['legOrigin']
            state.nearWaypoint = item['nearWaypoint']
            if state.noLegSet:      #This sets the starting position equal to the first waypoint
                state.currentPos = state.legOrigin.getPosition()
            state.noLegSet = False
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
    legGoalPos = state.legGoal.getPosition()
    legOriginPos = state.legOrigin.getPosition()
    #Run update of control laws
    # http://mathworld.wolfram.com/Point-LineDistance2-Dimensional.html
    # angle = math.atan2( (nextWP[1]-prevWP[1]),(nextWP[0]-prevWP[0] ) )
    # line  : ax + by + c = 0
    # coefficients
    # a=(yB−yA) , b=(xA−xB) and c=(xByA - xAyB)
    a = legGoalPos[1] - legOriginPos[1]
    b = legOriginPos[0] - legGoalPos[0]
    c = (legGoalPos[0] * legOriginPos[1]) - (legOriginPos[0] * legGoalPos[1])
    abDist = math.hypot(a,b)
    state.demandPos = legGoalPos
    if abDist < 1e-10 or state.currentPos == legGoalPos: return #avoid divide by zero
    distToLeg = (a*state.currentPos[0] + b*state.currentPos[1] + c ) / abDist
    # along perpendicular vector ( a , b )
    deltaXfromLeg = a * distToLeg / abDist
    deltaYfromLeg = b * distToLeg / abDist
    closePointOnLeg =  (state.currentPos[0] - deltaXfromLeg, state.currentPos[1] -  deltaYfromLeg)
    distToGoal = math.hypot( legGoalPos[0] - closePointOnLeg[0], legGoalPos[1] - closePointOnLeg[1] )
    absToLeg =  abs(distToLeg)
    moveAmount = distToGoal
    if absToLeg > distToGoal: moveAmount =  0
    #print "absToLeg", absToLeg, "dist: ", distToGoal
    # demandPos is a point on the Leg, maxMove along from closePointOnLeg
    state.demandPos = ( (legGoalPos[0] - closePointOnLeg[0]) / distToGoal * moveAmount + closePointOnLeg[0] , \
                    (legGoalPos[1] - closePointOnLeg[1]) / distToGoal * moveAmount + closePointOnLeg[1])

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
    brakingPct = round(min(100.0, dtgFactor)  ,0) # 100% = full speed
    if brakingPct < 10.0 : brakingPct = 0
    #TODO
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
    'demandPos':sourceState.demandPos,
    'nearWaypoint':sourceState.nearWaypoint}
    destQueue.put(message)


def angleDiff ( fromAngle, toAngle ) :
    angleDiff = toAngle - fromAngle
    if angleDiff > 180:
        angleDiff -= 360
    elif angleDiff < -180:
        angleDiff += 360
    return angleDiff
