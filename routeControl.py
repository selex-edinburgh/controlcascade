'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import time
import math
import threading
import datetime
from plumbing.observablestate import ObservableState
from plumbing.arcnode import ArcNodeObserverTranslator
from lib.navigation import *

class RouteState(ObservableState):
    def __init__(self, near):
        super(RouteState,self).__init__()
        self.nextWaypoint = 1
        WaypointManager.setWaypointType(WaypointTypeEnum.CONTINUOUS)
        self.waypoints    = [

##        WaypointManager.createWaypoint(2390,4630),
##        WaypointManager.createWaypoint(2390,4630)]
        
        #Estimate of course

##        WaypointManager.createWaypoint(2250,200),# Starting Position: Waypoint 0
##        WaypointManager.createWaypoint(2300,980),
##        WaypointManager.createWaypoint(1460,1030),
##        WaypointManager.createWaypoint(1480,1920),
##        WaypointManager.createWaypoint(2250,2010),
##        WaypointManager.createWaypoint(2300,2850), 
##        WaypointManager.createWaypoint(1240,2840),
##        WaypointManager.createWaypoint(470,6560),
##        WaypointManager.createWaypoint(1850,6750),
##        WaypointManager.createWaypoint(2270,5570),       
##        WaypointManager.createWaypoint(2270,4140),    
##        WaypointManager.createWaypoint(1210,2920),             
##        WaypointManager.createWaypoint(2410,2840),                       
##        WaypointManager.createWaypoint(2280,2040),                                  
##        WaypointManager.createWaypoint(1360,1860),                              
##        WaypointManager.createWaypoint(1310,1110),                              
##        WaypointManager.createWaypoint(2140,1030),                        
##        WaypointManager.createWaypoint(2300,220)
             
        #Square
##        WaypointManager.createWaypoint(1400, 3800),
##        WaypointManager.createWaypoint(1400, 5800),
##        WaypointManager.createWaypoint(3400, 5800),
##        WaypointManager.createWaypoint(3400, 3800),
##        WaypointManager.createWaypoint(1400, 3800)

        #FigureofEight
        WaypointManager.createWaypoint(1400, 3800),
        WaypointManager.createWaypoint(1400, 4800),
        WaypointManager.createWaypoint(2400, 4800),
        WaypointManager.createWaypoint(2400, 5800),
        WaypointManager.createWaypoint(1400, 5800),
        WaypointManager.createWaypoint(1400, 4800),
        WaypointManager.createWaypoint(2400, 4800),
        WaypointManager.createWaypoint(2400, 3800),
        WaypointManager.createWaypoint(1400, 3800),
        WaypointManager.createWaypoint(1400, 4000)
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
                #print "near {} {}".format(dist, tempWaypoint) 
                if tempWaypoint.waitPeriod !=0: 
                    currentTime = datetime.datetime.utcnow() # sets current time to whatever the time is on the loop
                    if not(state.waiting): # Check to see if wait has started if not start waiting
                        state.waiting = True
                        state.goalTime = currentTime + datetime.timedelta(0,tempWaypoint.waitPeriod) # adds a delta to the current time. timedelta(days,seconds)

                    if state.waiting and state.goalTime <= currentTime: # Check to see if currentTime is past goalTime
                        state.waiting = False # Reseting the wait

                if not(state.waiting):
                    #print "Setting waypoint {}".format(tempWaypoint)
                    state.nearWaypoint = tempWaypoint
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
