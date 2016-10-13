import time
import math
import threading
import datetime
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator
from lib.navigation import *

class RouteState(ObservableState):
    def __init__(self, near):
        super(RouteState,self).__init__()
        self.nextWaypoint = 1
        WaypointManager.setWaypointType(WaypointTypeEnum.CONTINUOUS)
        self.waypoints    = [

##        (2390.0,4630.0),(2390.0,4630.0)]
        
        #Estimate of course

##        (2250.0,200.0),
##        (2300.0,980.0),
##        (1460.0,1030.0),
##        (1480.0,1920.0),
##        (2250.0,2010.0),
##        (2300.0,2850.0), 
##        (1240.0,2840.0),
##        (470.0,6560.0),
##        (1850.0,6750.0),
##        (2270.0,5570.0),       
##        (2270.0,4140.0),    
##        (1210.0,2920.0),             
##        (2410.0,2840.0),                       
##        (2280.0,2040.0),                                  
##        (1360.0,1860.0),                              
##        (1310.0,1110.0),                              
##        (2140.0,1030.0),                        
##        (2300.0,220.0)
             
        #Square
        WaypointManager.createWaypoint(2000, 4000),
        WaypointManager.createWaypoint(2000, 5000),
        WaypointManager.createWaypoint(3000, 5000),
        WaypointManager.createWaypoint(3000, 4000),
        WaypointManager.createWaypoint(2000, 4000)
        ]
        self.currentPos   = self.waypoints[0]
        self._near = near        # 120.0
        self.nearWaypoint = True
        self.timeStampFlow["control"]    = time.time()
        self.finalWaypoint = False
        self.goalTime = 0
        #self.routeChanged = True # to be set when waypoint are added/removed/modified : used/cleared by route to visual translator
        self.waiting = False
def routeControlUpdate(state,batchdata):
    #nearWaypointLocal = state.nearWaypoint
    for item in batchdata:
        if item['messageType'] == 'newWaypoint':
            newWaypoint = item['newWaypoint']
            state.waypoints.append(newWaypoint)
        elif item['messageType'] == 'removeWaypoint':
            state.waypoints.pop()
        elif item['messageType'] == 'sense': # TODO
            state.nearWaypoint = False
            sensedPos = item['sensedPos']
            tempWaypoint = state.waypoints[state.nextWaypoint] # store current waypoint locally
            dist = math.hypot(sensedPos[0] - tempWaypoint.getPosition()[0], sensedPos[1] - tempWaypoint.getPosition()[1]) # calculate distance to go to next waypoint
            if dist < state._near:

                if tempWaypoint.waitPeriod !=0: 
                    currentTime = datetime.datetime.utcnow() # sets current time to whatever the time is on the loop
                    if not(state.waiting): # Check to see if wait has started if not start waiting
                        state.waiting = True
                        state.goalTime = currentTime + datetime.timedelta(0,tempWaypoint.waitPeriod) # adds a delta to the current time. timedelta(days,seconds)

                    if state.waiting and state.goalTime <= currentTime: # Check to see if currentTime is past goalTime
                        state.waiting = False # Reseting the wait

                if not(state.waiting):    
                    state.nearWaypoint = True
                    if ( state.nextWaypoint+1 < len(state.waypoints)):
                        state.nextWaypoint += 1

                
def routeToTrackTranslator( sourceState, destState, destQueue ):
    nextID = sourceState.nextWaypoint      
    
    message = {'messageType':'control',
               'legGoal'    :sourceState.waypoints[nextID],
               'legOrigin'  :sourceState.waypoints[nextID-1],
               'timeStamp'  :sourceState.timeStampFlow["control"],
               'nearWaypoint' :sourceState.nearWaypoint
               }
  
    destQueue.put(message)

def routeToVisualTranslator( sourceState, destState, destQueue ): #TODO
##    if sourceState.routeChanged:
##        sourceState.routeChanged = False ## ??
##        send waypoint list etc
##        pass
##    nextID = sourceState.nextWaypoint      
    
    message = {'messageType':'waypointList',
               'waypointList' : sourceState.waypoints
               }
  
    destQueue.put(message)
