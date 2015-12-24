# -*- coding: utf-8 -*-
import time
import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

trackState = ObservableState()
#leg == line ending at next waypoint on route
#trackState.legTheta  = 0.0
trackState.noLegSet = True
trackState._trackUnitsToMm = 310.0 / 2.0    # use half of wheel track as tracking unit
trackState._movementBudget = math.pi / 2.0  # budget allows for turning pi/2 or more with no forward movement
trackState.legCoeff  = (0.0,0.0,0.0)        #in track units
trackState.legGoal = (0.0,0.0)              #in track units
trackState.currentTheta = math.pi / 2.0
trackState.currentPos = (0.0,0,0)           #in track units
trackState.demandTheta = math.pi / 2.0
trackState.demandPos = (0.0,0,0)            #in track units
trackState.timeStamp    = time.time()

def trackControlUpdate(state,batchdata):
    #process items in batchdata
    for item in batchdata:
        if item['messageType'] == 'control':
            print "Leg goal ",  trackUnitsToMm(state.legGoal)
            print "Current pos ", trackUnitsToMm(state.currentPos)
            print "Demand pos", trackUnitsToMm(state.demandPos)
            state.noLegSet = False
            #convert to track units
            state.legGoal = mmToTrackUnits(item['legGoal'])
            legOrigin =     mmToTrackUnits(item['legOrigin'])
            # angle = math.atan2( (nextWP[1]-prevWP[1]),(nextWP[0]-prevWP[0] ) )
            # line  : ax + by + c = 0
            # coefficients
            # a=(yB−yA) , b=(xA−xB) and c=(xByA - xAyB)
            state.legCoeff = ( ( state.legGoal[1] - legOrigin[1] ) ,
                                     ( legOrigin[0] - state.legGoal[0] ),
                                     ( state.legGoal[0] * legOrigin[1] - legOrigin[0] * state.legGoal[1] ) )        
            print 'track - control message'

        elif item['messageType'] == 'sense': ### integrate batch entries : sensedMove, sensedTurn
            #print 'track - sense message'
            #approximate as movement along circular arc, effective direction being mid-way on arc
            
            halfArcTurn = (item['sensedTheta']-state.currentTheta) / 2.0
            halfArcMove = (item['sensedMove']/state._trackUnitsToMm) / 2.0
            
            if halfArcTurn < 0.1:  # small angle approximation sin(theta) = theta : and avoid divide-by-zero risk
                linearMove = abs(2.0 * halfArcMove )
            else:
                linearMove = abs(2.0 * math.sin(halfArcTurn ) * halfArcMove / halfArcTurn) # linear move is shorter than arc
            midwayTheta = state.currentTheta + halfArcTurn
            state.currentPos = (state.currentPos[0] + linearMove * math.cos(midwayTheta), # x move along effective direction
                                    state.currentPos[1] + linearMove * math.sin(midwayTheta)) # y move along effective direction
            state.currentTheta = item['sensedTheta']
            state.timeStamp = time.time()
    if len(batchdata) == 0: return #do nothing here, unless new control or sense messages have arrived
    #Run update of control laws
    # http://mathworld.wolfram.com/Point-LineDistance2-Dimensional.html
    a = state.legCoeff[0]
    b = state.legCoeff[1]
    c = state.legCoeff[2]
    abDist = math.hypot(a,b)
    if abDist < 1e-10 or state.currentPos == state.legGoal: return #avoid divide by zero
    distToLeg = (a*state.currentPos[0] + b*state.currentPos[1] + c ) / abDist
    # along perpendicular vector ( a , b )
    deltaXfromLeg = a * distToLeg / abDist
    deltaYfromLeg = b * distToLeg / abDist
    closePointOnLeg =  (state.currentPos[0] - deltaXfromLeg, state.currentPos[1] -  deltaYfromLeg)
    distToGoal = math.hypot( state.legGoal[0] - closePointOnLeg[0], state.legGoal[1] - closePointOnLeg[1] )
    useableBudget = min(distToGoal,state._movementBudget)
    # legTarget is a point on the Leg, useableBudget along from closePointOnLeg
    legTarget = ( (state.legGoal[0] - closePointOnLeg[0]) / distToGoal * useableBudget + closePointOnLeg[0] , \
                    (state.legGoal[1] - closePointOnLeg[1]) / distToGoal * useableBudget + closePointOnLeg[1])
    # of useableBudget, subtract necessary rotation
    state.demandTheta = math.atan2( legTarget[1] - state.currentPos[1] , legTarget[0] - state.currentPos[0] )
    rotation = angleDiff( state.currentTheta, state.demandTheta )
        # could constrain rotation to use useable budget
    deltaXtoLegTarget = legTarget[0] - state.currentPos[0] 
    deltaYtoLegTarget = legTarget[1] - state.currentPos[1]
    distToLegTarget = math.hypot(deltaXtoLegTarget ,deltaYtoLegTarget )
    useableBudget = min(max(useableBudget - abs(rotation), 0),distToLegTarget)
    if distToLegTarget < 1e-10:
        scaleXtoBudget = deltaXtoLegTarget
        scaleYtoBudget = deltaYtoLegTarget
    else:
        scaleXtoBudget = deltaXtoLegTarget * useableBudget / distToLegTarget
        scaleYtoBudget = deltaYtoLegTarget * useableBudget / distToLegTarget
    state.demandPos = (state.currentPos[0] + scaleXtoBudget, \
                            state.currentPos[1] + scaleYtoBudget)
    

                    

def mmToTrackUnits( point ):
  return ( point[0] / trackState._trackUnitsToMm, point[1] / trackState._trackUnitsToMm)

def trackUnitsToMm( point ):
  return ( point[0] * trackState._trackUnitsToMm, point[1] * trackState._trackUnitsToMm)



def trackToRouteTranslator( sourceState, destState, destQueue ):
    message = {'messageType':'sense','sensedPos':trackUnitsToMm(sourceState.currentPos)}
    destQueue.put(message)

def trackToRcChanTranslator( sourceState, destState, destQueue ):

    fwd = math.hypot(sourceState.demandPos[0]-sourceState.currentPos[0],
                      sourceState.demandPos[1]-sourceState.currentPos[1]) / sourceState._movementBudget
    turn = angleDiff(sourceState.currentTheta, sourceState.demandTheta) / sourceState._movementBudget
    
    message = {'messageType':'control','demandTurn':turn,
                                       'demandFwd':fwd }
    destQueue.put(message)

def angleDiff ( fromTheta, toTheta ) :
    thetaDiff = sourceState.toTheta - sourceState.fromTheta
    if thetaDiff > math.pi:
        thetaDiff -= math.pi * 2.0
    elif thetaDiff < -math.pi:
        thetaDiff += math.pi * 2.0

########### stub test routine

testCounter = 1.0
testWorkerRunning = False

def testTrackObsTranStub( sourceState, destState, destQueue ):
    def testWorker():
        global testCounter
        demandToMeet = 0.05
        while testWorkerRunning:
            thetaDiff = angleDiff( sourceState.currentTheta , sourceState.demandTheta )
            thetaSense = sourceState.currentTheta + thetaDiff * demandToMeet
            dist = math.hypot(sourceState.demandPos[0]-sourceState.currentPos[0],
                                                   sourceState.demandPos[1]-sourceState.currentPos[1])
            distSense = (dist * demandToMeet) *sourceState._trackUnitsToMm
            destQueue.put({'messageType':'sense',
                           'sensedMove':distSense,
                           'sensedTheta':thetaSense}) 
            testCounter += 0.0
            time.sleep(0.05)
    global testWorkerRunning, testCounter 
    if not testWorkerRunning and not sourceState.noLegSet:
        th = threading.Thread(target=testWorker)
        th.daemon = True
        testWorkerRunning = True
        th.start()
    testCounter = 1.0
    
      
    
