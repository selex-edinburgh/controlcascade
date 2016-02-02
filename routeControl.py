import time
import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

class RouteState(ObservableState):
    def __init__(self, near):
        super(RouteState,self).__init__()
        self.nextWaypoint = 1
        self.waypoints    = [ (1200.0,0.0),
                                (1390.0,210.0),
                                (2250.0,200.0),
                                (2300.0,980.0),
                                (1460.0,1030.0),
                                (1480.0,1920.0),
                                (2250.0,2010.0),
                                (2300,2850), 
                                (1240.0,2840.0),
                                (470.0,6560.0),
                                (1850.0,6750.0),
                                (2270.0,5570.0),       
                                (2270.0,4140.0),    
                                (1210.0,2920.0),             
                                (2410.0,2840.0),                       
                                (2280.0,2040.0),                                  
                                (1360.0,1860.0),                              
                                (1310.0,1110.0),                              
                                (2140.0,1030.0),                        
                                (2300.0,220.0)]
        self.currentPos   = self.waypoints[0]
        self._near = near #120.0
        self.timeStamp    = time.time()

def routeControlUpdate(state,batchdata):
    for item in batchdata:
        if item['messageType'] == 'control':
            print 'route - control message'
        elif item['messageType'] == 'sense':
            #print 'route - sense message'
            sensedPos = item['sensedPos']
            distToWPx = sensedPos[0] - state.waypoints[state.nextWaypoint][0]
            distToWPy = sensedPos[1] - state.waypoints[state.nextWaypoint][1]
            dist = math.hypot( distToWPx , distToWPy )
            #TODO - appropriate distance check for waypoint-reached?
            if dist < state._near: 
                print dist, sensedPos, state.waypoints[state.nextWaypoint]
                print '******************************waypoint reached'
                if ( state.nextWaypoint+1 < len(state.waypoints)):
                    state.nextWaypoint += 1 
                

def routeToTrackTranslator( sourceState, destState, destQueue ):
    nextID = sourceState.nextWaypoint
    message = {'messageType':'control',
               'legGoal'    :sourceState.waypoints[nextID],
               'legOrigin'  :sourceState.waypoints[nextID-1]}
    #print message
    destQueue.put(message)

      
    
