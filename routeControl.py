'''
Copyright (c) 2017 Leonardo MW Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software in a limited manner. Permissions to publish, distribute, sublicense or sell the Software are not granted. Permissions granted are: the rights to use, copy, modify and merge copies of the Software solely within the context of the "Rampaging Chariots" educational project, and subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

'''
Section 1
Green Block
'''
import time
import math
import threading
import datetime
from plumbing.observablestate import ObservableState
from plumbing.arcnode import ArcNodeObserverTranslator
from functools import partial
from lib.navigation import *
from lib.sensoractions import *

class RouteState(ObservableState):
    def __init__(self, near):
        '''
        Section 2
        Green Block
        '''
        super(RouteState,self).__init__()
        self.nextWaypoint = 1
        WaypointManager.setWaypointType(WaypointTypeEnum.CONTINUOUS)

        bus = I2C(defaultAddress=4)
        irStepper = ScanningSensor(IR(bus), StepperMotor(bus), 'irStepper')
        makeSensor_Triangulate = makeTriangulator(scanningSensor=irStepper, scanAngleWidth=20, scanNo=5, scanSpeed=1, scanningSensor2=irStepper, scanAngleWidth2=20, scanNo2=5, scanSpeed2=1) # populates makeTriangulate with the create function from makeTriangulator, with some defaulted values
                                                                                                            # this means that a scanAction can be made from just a pair of coordinates  having theses defaulted values filling the rest
        self.waypoints    = [

##        Waypoint(2390,4630, 0),     #(x, y, waitPeriod)
##        Waypoint(2390,4630, 0)
        
        #Estimate of course

##        Waypoint(2250,200, 0),      #(x, y, waitPeriod)
##        Waypoint(2300,980, 0),
##        Waypoint(1460,1030, 0),
##        Waypoint(1480,1920, 0),
##        Waypoint(2250,2010, 0),
##        Waypoint(2300,2850, 0), 
##        Waypoint(1240,2840, 0),
##        Waypoint(470,6560, 0),
##        Waypoint(1850,6750, 0),
##        Waypoint(2270,5570, 0),       
##        Waypoint(2270,4140, 0),    
##        Waypoint(1210,2920, 0),             
##        Waypoint(2410,2840, 0),                       
##        Waypoint(2280,2040, 0),                                  
##        Waypoint(1360,1860, 0),                              
##        Waypoint(1310,1110, 0),                              
##        Waypoint(2140,1030, 0),                        
##        Waypoint(2300,220, 0)
             
##        #Square
##        Waypoint(1400, 3800, 0),#(x, y, waitPeriod, [makeTriangulate(makeScan(scanningSensor1, ((x1,y1),objRadius1), scanAngleWidth1, scanNo1, scanSpeed1), makeScan(scanningSensor2, ((x2,y2),objRadius2), scanAngleWidth2, scanNo2, scanSpeed2))])
##        Waypoint(1400, 5800, 10, [makeSensor_Triangulate(((1900,6300),0), ((900,6300),0))]),#(x,y, waitPeriod, [makeSensor_Triangulate(((x1,y1),objRadius1),((x2,y2),objRadius2))]  
##        Waypoint(3400, 5800, 0),
##        Waypoint(3400, 3800, 0),
##        Waypoint(1400, 3800, 0)

        #scan test
        Waypoint(1400, 3800, 0),#(x, y, waitPeriod, [makeTriangulate(makeScan(scanningSensor1, ((x1,y1),objRadius1), scanAngleWidth1, scanNo1, scanSpeed1), makeScan(scanningSensor2, ((x2,y2),objRadius2), scanAngleWidth2, scanNo2, scanSpeed2))])
        Waypoint(1400, 4800, 20, [makeSensor_Triangulate(((1900,5300)),0), ((900,5300),0)))]),#(x,y, waitPeriod, [makeSensor_Triangulate(((x1,y1),objRadius1), ((x2,y2),objRadius2))]  
        Waypoint(2400, 4800, 0)
        
        #FigureofEight
##        Waypoint(1400, 3800, 0),    #(x, y, waitPeriod, actions[sensorType, x, y, scanAngle, scanNo])
##        Waypoint(1400, 4800, 0),
##        Waypoint(2400, 4800, 0),
##        Waypoint(2400, 5800, 0),
##        Waypoint(1400, 5800, 0),
##        Waypoint(1400, 4800, 0),
##        Waypoint(2400, 4800, 0),
##        Waypoint(2400, 3800, 0),
##        Waypoint(1400, 3800, 0),
##        Waypoint(1400, 4000, 0)
        ]
        self.currentPos = self.waypoints[0]
        self._near = near        # 120.0 The detection radius of when the chariot has reached a waypoint
        self.nearWaypoint = True
        self.timeStampFlow["control"] = time.time()
        self.finalWaypoint = False
        self.goalTime = 0
        #self.routeChanged = True # to be set when waypoint are added/removed/modified : used/cleared by route to visual translator
        self.waiting = False
        self.runActions = None
        
def routeControlUpdate(state,batchdata):
    '''
    Section 3
    Green Block
    '''
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
            '''
            Section 4
            Amber Block
            '''
            state.runActions = None
            if dist < state._near:
                #print "near {} {}".format(dist, tempWaypoint) 
                if tempWaypoint.waitPeriod !=0: 
                    currentTime = datetime.datetime.utcnow() # sets current time to whatever the time is on the loop
                    if not state.waiting: # Check to see if wait has started if not start waiting
                        state.waiting = True
                        state.goalTime = currentTime + datetime.timedelta(0,tempWaypoint.waitPeriod) # adds a delta to the current time. timedelta(days,seconds)
                        state.runActions = state.waypoints[sourceState.nextWaypoint].actions
                    if state.waiting and state.goalTime <= currentTime: # Check to see if currentTime is past goalTime
                        state.waiting = False # Reseting the wait

                if not state.waiting:
                    #print "Setting waypoint {}".format(tempWaypoint)
                    state.nearWaypoint = tempWaypoint
                    if ( state.nextWaypoint+1 < len(state.waypoints)):
                        state.nextWaypoint += 1

'''
Section 5
Green Block
'''                
def routeToTrackTranslator( sourceState, destState, destQueue ):
    nextID = sourceState.nextWaypoint      
    
    message = {'messageType':'control',
               'legGoal'    :sourceState.waypoints[nextID],
               'legOrigin'  :sourceState.waypoints[nextID-1],
               'timeStamp'  :sourceState.timeStampFlow["control"],
               'nearWaypoint' :sourceState.nearWaypoint
               }
    destQueue.put(message)

def routeToSensorTranslator( sourceState, destState, destQueue ):
    if sourceState.runActions !=  None:
        message = {'messageType':'scan',
                   'actions'    :sourceState.runActions
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
