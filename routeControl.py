import time
import math
import threading
from plumbing.observablestate import ObservableState
from plumbing.controlloop import ControlObserverTranslator

routeState = ObservableState()
routeState.nextWaypoint = 1
routeState.waypoints    = [ (0.0,0.0),
                           (0.0,300.0),
                           (1000.0,500.0),
                           (1000.0,1000.0),
                           (1550.0,1550.0),
                           (1200.0,200.0),
                           (2000.0,1000.0),
                           (4000,2000),
                            #(3990.00833055605,2199.66683329366),
                            (3960.13315568248,2397.33866159012),
                            #(3910.67297825121,2591.04041332268),
                            (3842.12198800577,2778.8366846173),
                            #(3755.16512378075,2958.85107720841),
                            (3650.67122981936,3129.28494679007),
                            #(3529.68437456898,3288.43537447538),
                            (3393.41341869433,3434.71218179905),
                            #(3243.21993654133,3566.65381925497),
                            (3080.60461173628,3682.94196961579),
                            #(2907.19224285115,3782.41472012287),
                            (2724.71550895335,3864.07817193445),
                            #(2534.99765724917,3927.11637083439),
                            (2339.93428580048,3970.89945997692),
                            #(2141.47440333541,3994.98997320811),
                            (1941.60095539742,3999.14720608301),
                            #(1742.31101140895,3983.32962090494),
                            (1545.59581061383,3947.69526175639),
                            #(1353.42086627299,3892.60017537483),
                            (1167.70632690572,3818.59485365136),
                            #(990.307790800285,3726.41873329775),
                            (822.997765489308,3616.99280763918),
                            #(667.447957440352,3491.41042435344),
                            (525.212568917509,3350.9263611023),
                            #(397.712768906133,3196.94428820791),
                            (286.222493262105,3031.00274364293),
                            #(191.855715965878,2854.75976046766),
                            (115.555318662684,2669.97630031181),
                            #(58.083669700819,2478.49865842796),
                            (20.0150067991092,2282.24001611973),
                            #(1.72969945344107,2083.16132486658),
                            (3.4104484104937,1883.25171314484),
                            #(25.0404601822702,1684.5086117135),
                            (66.4036148410778,1488.91779594634),
                           (2000.0,1200.0),
                           (2200.0,1300.0),
                           (3000.0,4500.0),
                           (3000.0,3000.0),
                           (0.0,1300.0)]
routeState.currentPos   = routeState.waypoints[0]
routeState.timeStamp    = time.time()

near = 160.0

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
            if dist < near: 
                print dist, sensedPos, state.waypoints[state.nextWaypoint]
                print '******************************waypoint reached'
                if ( state.nextWaypoint+1 < len(state.waypoints)):
                    state.nextWaypoint += 1 
                

def routeToTrackTranslator( sourceState, destState, destQueue ):
    nextID = sourceState.nextWaypoint
    message = {'messageType':'control',
               'legGoal'    :sourceState.waypoints[nextID],
               'legOrigin'  :sourceState.waypoints[nextID-1]}
    print message
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
        th.daemon = True
        testWorkerRunning = True
        th.start()
        
    testCounter = 0.0
    
      
    
