import time
import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

routeState = ObservableState()
routeState.nextWaypoint = 1
routeState.waypoints    = [(1000.0,500.0),(1000.0,1000.0),(1550.0,1550.0),(2000.0,1000.0),(3000.0,3000.0),(0.0,1300.0)]
routeState.currentPos   = routeState.waypoints[0]
routeState.timeStamp    = time.clock()


def routeControlUpdate(routeState,batchdata):
    for item in batchdata:
        if item['messageType'] == 'control':
            print 'route - control message'
        elif item['messageType'] == 'sense':
            #print 'route - sense message'
            sensedPos = item['sensedPos']
            distToWPx = sensedPos[0] - routeState.waypoints[routeState.nextWaypoint][0]
            distToWPy = sensedPos[1] - routeState.waypoints[routeState.nextWaypoint][1]
            dist = math.hypot( distToWPx , distToWPy )
            #TODO - appropriate distance check for waypoint-reached?
            if dist < 50.0: 
                print dist, sensedPos, routeState.waypoints[routeState.nextWaypoint]
                print '******************************waypoint reached'
                if ( routeState.nextWaypoint+1 < len(routeState.waypoints)):
                    routeState.nextWaypoint += 1 
                

def routeToTrackTranslator( sourceState, destState, destQueue ):
    nextID = sourceState.nextWaypoint
    message = {'messageType':'control',
               'legGoal'    :sourceState.waypoints[nextID],
               'legOrigin'  :sourceState.waypoints[nextID-1]}
    destQueue.put(message)



############ test method

testCounter = 0.0
testWorkerRunning = False

def testRouteObsTranStub( sourceState, destState, destQueue ):
    def testWorker():
        global testCounter
        while testWorkerRunning:
            #print 'tock'
            lastWP = sourceState.waypoints[sourceState.nextWaypoint-1]
            nextWP = sourceState.waypoints[sourceState.nextWaypoint]
            x = lastWP[0] + testCounter * (nextWP[0] - lastWP[0])
            y = lastWP[1] + testCounter * (nextWP[1] - lastWP[1])
            destQueue.put({'messageType':'sense','sensedPos':(x,y)})
            testCounter = min ( testCounter + 0.01, 1.0 )
            time.sleep(0.1)
    print 'testRouteControlStub'
    global testWorkerRunning, testCounter 
    if not testWorkerRunning:
        th = threading.Thread(target=testWorker)
        th.daemon = true
        testWorkerRunning = True
        th.start()
        
    testCounter = 0.0
    
      
    
