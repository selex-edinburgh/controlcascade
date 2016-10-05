import time
import math
import threading
import datetime
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class RouteState(ObservableState):
    def __init__(self, near, waitPeriod):
        super(RouteState,self).__init__()
        self.nextWaypoint = 1
        self.waypoints    = [
        
        #                   (2390.0,4630.0),(2390.0,4630.0)]
        
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
        (2000, 4000),
        (2000, 5000),
        (3000, 5000),
        (3000, 4000),
        (2000, 4000)
        ]
        self.currentPos   = self.waypoints[0]
        self._near = near        # 120.0
        self.nearWaypoint = True
        self.timeStampFlow["control"]    = time.time()
        self.finalWaypoint = False
        self.goalTime = 0
        #self.routeChanged = True # to be set when waypoint are added/removed/modified : used/cleared by route to visual translator
        self.waitPeriod = waitPeriod
        self.waiting = False
def routeControlUpdate(state,batchdata):
    #nearWaypointLocal = state.nearWaypoint
    for item in batchdata:
        if item['messageType'] == 'waypoint':
            newWaypoint = tuple(10*x for x in item['newWaypoint'])
            state.waypoints.append(newWaypoint)
            for item['removeWaypoint'] in batchdata:
                if item['removeWaypoint'] == True:
                    state.waypoints.pop()
                    print "Waypoint Removed"

        elif item['messageType'] == 'sense':
            state.nearWaypoint = False
            sensedPos = item['sensedPos']
            distToWPx = sensedPos[0] - state.waypoints[state.nextWaypoint][0]
            distToWPy = sensedPos[1] - state.waypoints[state.nextWaypoint][1]
            dist = math.hypot( distToWPx , distToWPy )
            if dist < state._near:

                if state.waitPeriod!=0: 
                    currentTime = datetime.datetime.utcnow() # sets current time to whatever the time is on the loop
                    if not(state.waiting): # Check to see if wait has started if not start waiting
                        state.waiting = True
                        state.goalTime = currentTime + datetime.timedelta(0,state.waitPeriod) # adds a delta to the current time. timedelta(days,seconds)

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

def routeToVisualTranslator( sourceState, destState, destQueue ):
    #if sourceState.routeChanged:
    #    sourceState.routeChanged = False ## ??
        #send waypoint list etc
        pass
    #nextID = sourceState.nextWaypoint      
    
    #message = {'messageType':'control',
    #           'legGoal'    :sourceState.waypoints[nextID],
    #           'legOrigin'  :sourceState.waypoints[nextID-1],
    #           'timeStamp'  :sourceState.timeStampFlow["control"],
    #           'nearWaypoint' :sourceState.nearWaypoint
    #           }
  
    #destQueue.put(message)
