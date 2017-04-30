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
from plumbing.arcnode import ArcNodeObserverTranslator
from lib.navigation import *

class TrackState(ObservableState):
    def __init__(self, wheelBase, trackWidth, movementBudget, xPos1, yPos1, xPos2, yPos2, underTurn):
        super(TrackState,self).__init__()

        self.noLegSet = True
        self.legGoal = WaypointManager.createWaypoint(xPos2,yPos2)
        self.legOrigin = WaypointManager.createWaypoint(xPos1,yPos1)
        self.currentAngle = 0
        #self.currentPos = (2390.0,4630.0) # Uncomment this line to have RC draw at centre of screen
        self.currentPos = (xPos1,yPos1)  # This draws the RC off screen before clicking Start
        self.demandAngle = 0
        self.demandPos = (0.0,0.0)
        self._trackWidth = trackWidth                   # nominal 237.0 mm between wheels l/r
        self._wheelBase = wheelBase                     # nominal 200.0 mm between wheels f/b
        self.turnRadius = math.hypot(self._trackWidth, self._wheelBase)/2.0 # value should be around 155.0 mm
        self.turnFactor = ((self._trackWidth/2.0)/self.turnRadius)**2.0 # takes into account the turning component
        # and the turn radius to create a correction value that can be applied to the heading (0.58)
        self.underTurn = underTurn
        #self._movementBudget = movementBudget       # 500.0 mm
        self.timeStamp = time.time()
        self.timeStampFlow["control"] = time.time()
        self.timeStampFlow["sense"] = time.time()
        #self.pole = (1200,0)
        #self.isCollision = False
        self.nearWaypoint = False       # check is near next waypoint
        self.demandTurn = None
        self.demandFwd = None
        self.driveMode = 'Parked'
        self.hdg2Go = 0.0
        self.dist2Go = 0
        self.hdgGone = 0.0
        self.distGone = 0
        self.latPhase = 'end'
        self.longPhase = 'reset'
        self.requestWaypoint = False
def trackControlUpdate(state,batchdata):
    for item in batchdata:      # Process items in batchdata
        if 'timeStamp' not in item:
            pass
        else:
            state.timeStampFlow[item['messageType']] = item['timeStamp']

        if item['messageType'] == 'control':
            state.legGoal = item['legGoal']
            state.legOrigin = item['legOrigin']
            state.requestWaypoint = item['requestWaypoint']
            state.nearWaypoint = item['nearWaypoint']
            state.latPhase = item['latPhase']
            state.longPhase = item['longPhase']
            if state.noLegSet:      #This sets the starting position equal to the first waypoint
                state.currentPos = state.legOrigin.getPosition()
            state.noLegSet = False
        elif item['messageType'] == 'phase':
            state.latPhase = item['latPhase']
            state.longPhase = item['longPhase']
        elif item['messageType'] == 'sense': ### integrate batch entries : sensedMove, sensedTurn
            #approximate as movement along circular arc, effective direction being mid-way on arc

            halfArcTurn = (item['sensedAngle']-state.currentAngle) / 2.0
            halfArcMove = (item['sensedMove']) / 2.0

            if math.radians(halfArcTurn) < 0.1:  # small angle approximation sin(angle) = angle : and avoid divide-by-zero risk
                linearMove = (2.0 * halfArcMove )
            else:
                linearMove = (2.0 * math.sin(math.radians(halfArcTurn) ) * halfArcMove / math.radians(halfArcTurn)) # linear move is shorter than arc

            midwayAngle = state.currentAngle + halfArcTurn
##            state.currentPos = (state.currentPos[0] + linearMove * math.sin(math.radians(midwayAngle)), # x move along effective direction
##                                   state.currentPos[1] + linearMove * math.cos(math.radians(midwayAngle))) # y move along effective direction
            state.currentAngle = item['sensedAngle']
            
#START ignore all that ^^^
#   just turn first, then move
            move = item['sensedMove']
            oldpos = state.currentPos
            
            state.currentPos = ( oldpos[0] + move * math.cos(math.radians(90-state.currentAngle)),
                                  oldpos[1] + move * math.sin(math.radians(90-state.currentAngle)) )
##            print 'track'
##            print 'oldPos', oldpos
##            print 'currentPos', state.currentPos

#END end ignore all that ^^^
            
            state.timeStamp = time.time()

    if len(batchdata) == 0: return      # do nothing here, unless new control or sense messages have arrived

    legGoalPos = state.legGoal.getPosition()
    legOriginPos = state.legOrigin.getPosition()

    if (state.latPhase == "end") and (state.longPhase == "end"): #both turn & line completed
        state.requestWaypoint = True

##    print 'track'
##    print 'currentPos0', state.currentPos[0]
##    print 'legGoalPos0', legGoalPos[0]
##    print 'currentPos1', state.currentPos[1]
##    print 'legGoalPos1', legGoalPos[1]

    state.dist2Go = math.hypot(state.currentPos[0] - legGoalPos[0], state.currentPos[1] - legGoalPos[1])              #distance to go to next wpt
    legGoalHdgRadians = math.atan2(legGoalPos[1] - state.currentPos[1], legGoalPos[0] - state.currentPos[0])    #wptHdg= math.atan2(y,x) (radians)
    legGoalHdgDegrees = math.degrees(legGoalHdgRadians)
    legGoalHdg = (90 - legGoalHdgDegrees)%360           #compass wrt North +ve clockwise
    state.hdg2Go = angleDiff(state.currentAngle, legGoalHdg)  #heading to turn to face next wpt

    state.distGone = math.hypot(state.currentPos[0] - legOriginPos[0], state.currentPos[1] - legOriginPos[1])              #distance gone towards next wpt
    legOriginHdgRadians = math.atan2(legOriginPos[1] - state.currentPos[1], legOriginPos[0] - state.currentPos[0])    #wptHdg= math.atan2(y,x) (radians)
    legOriginHdgDegrees = math.degrees(legOriginHdgRadians)
    legOriginHdg = (90 - legOriginHdgDegrees)%360           #compass wrt North +ve clockwise
    state.hdgGone = angleDiff(state.currentAngle, legOriginHdg)  #heading turned towards next wpt
    
##    print 'track'
##    print 'currentPos', state.currentPos, 'legGoalPos', legGoalPos
##    print 'legGoalHdgDegrees', legGoalHdgDegrees
##    print 'currentAngle', state.currentAngle, 'legGoalHdg', legGoalHdg
##    print 'hdg2Go', state.hdg2Go, 'dist2Go', state.dist2Go
##    print 'hdgGone', state.hdgGone, 'distGone', state.distGone
##    print ' '
    
    if state.hdg2Go > 0 and state.latPhase <> 'end':        #action turnRt
        state.driveMode = 'TurnR'
    elif state.hdg2Go < 0 and state.latPhase <> 'end':      #action turnLt 
        state.driveMode = 'TurnL'
    elif state.dist2Go > 0 and state.longPhase <> 'end':    #action moveFwd
        state.driveMode = 'MoveFwd'
    else: ##if state.hdg2Go == 0 and state.dist2Go == 0:    #no movement
        state.driveMode = 'Parked'
    
##    #Run update of control laws
##    # http://mathworld.wolfram.com/Point-LineDistance2-Dimensional.html
##    # A = legOriginPos, B = legGoalPos
##    # line  : ax + by + c = 0 : (1) mathworld link
##    # coefficients
##    # a=(yB-yA) , b=(xA-xB) and c=(xByA - xAyB)
##    a = legGoalPos[1] - legOriginPos[1]
##    b = legOriginPos[0] - legGoalPos[0]
##    c = (legGoalPos[0] * legOriginPos[1]) - (legOriginPos[0] * legGoalPos[1])
##    abDist = math.hypot(a,b)
##    state.demandPos = legGoalPos
##    if abDist < 1e-10 or state.currentPos == legGoalPos: return #avoid divide by zero
##    distToLeg = (a*state.currentPos[0] + b*state.currentPos[1] + c ) / abDist # distToLeg is distance to closePointOnLeg, Leg being the line from legOriginPos to legGoalPos : (11) mathworld link
##    
##    deltaXfromLeg = a * distToLeg / abDist # scaling values down from arbitrary magnitude (a,b) vector : (4) mathworld link
##    deltaYfromLeg = b * distToLeg / abDist # scaling values down from arbitrary magnitude (a,b) vector : (4) mathworld link
##    closePointOnLeg =  (state.currentPos[0] - deltaXfromLeg, state.currentPos[1] -  deltaYfromLeg) 
##    absToLeg =  abs(distToLeg) # absolute magnitude of distance to closest point on leg (closePointOnLeg)
##    distToGoal = math.hypot( legGoalPos[0] - closePointOnLeg[0], legGoalPos[1] - closePointOnLeg[1] ) # distance from closePointOnLeg to legGoalPos
##
##    moveAmount = distToGoal
##    if absToLeg > distToGoal: moveAmount =  0
##    # demandPos is a point on the Leg,
##    state.demandPos = ( (legGoalPos[0] - closePointOnLeg[0]) / distToGoal * moveAmount + closePointOnLeg[0] , \
##                    (legGoalPos[1] - closePointOnLeg[1]) / distToGoal * moveAmount + closePointOnLeg[1])
##    state.demandAngle = math.degrees(math.atan2( state.demandPos[0] -  state.currentPos[0] , state.demandPos[1] - state.currentPos[1] ))


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
    message = {'messageType':'sense',
               #'sensedPos':sourceState.currentPos
               'latPhase' :sourceState.latPhase,
               'longPhase' :sourceState.longPhase,
               'requestWaypoint':sourceState.requestWaypoint}
    destQueue.put(message)

def trackToRcChanTranslator( sourceState, destState, destQueue ):

##    dtgFactor = math.hypot(sourceState.demandPos[0]-sourceState.currentPos[0],
##                      sourceState.demandPos[1]-sourceState.currentPos[1] ) / 4.0#TODO dtg = distanceToGo
##    brakingPct = round(min(100.0, dtgFactor)  ,0) # 100% = full speed
##    if brakingPct < 10.0 : brakingPct = 0
##    #TODO
##    turn = angleDiff(sourceState.currentAngle, sourceState.demandAngle) / 90
##    move = max ( 1 - abs(turn), 0 )
##
##    message = {'messageType':'control','demandTurn': turn * brakingPct / 100.0,
##                                       'demandFwd' : move * brakingPct / 100.0,
##                                       'timeStamp' : sourceState.timeStampFlow["control"]
##                                       }
    
    message = {'messageType':'control','hdg2Go': sourceState.hdg2Go,
                                       'dist2Go' : sourceState.dist2Go,
                                       'hdgGone' : sourceState.hdgGone,
                                       'distGone' : sourceState.distGone,
                                       'driveMode' : sourceState.driveMode,
                                       'latPhase' : sourceState.latPhase,
                                       'longPhase' : sourceState.longPhase,
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
    'nextWaypoint':sourceState.legGoal,
    'nearWaypoint':sourceState.nearWaypoint}
    destQueue.put(message)
    
def trackToSensorTranslator(sourceState, destState, destQueue):
    message = {'messageType':'sensedRobot',
            'robotPos':sourceState.currentPos,
            'robotHdg':sourceState.currentAngle}
    destQueue.put(message)

def angleDiff ( fromAngle, toAngle ) :
    angleDiff = toAngle - fromAngle
    if angleDiff > 180:
        angleDiff -= 360
    elif angleDiff < -180:
        angleDiff += 360
    return angleDiff
