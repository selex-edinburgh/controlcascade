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
import plumbing.controlloop

import routeControl
import trackControl
import odoControl
import rcChanControl
import vsimControl
import envSimControl
import sensorControl
import visualControl
import statsControl
import scanSimControl

def runControlLoops():

    '''
    Section 2
    Green Block
    '''
    timeScale = 1
    guiTimeScale = 0.5

    trackUpdateRateMin = 0.016
    trackUpdateRateMax =   1

    odoUpdateRateMin = 0.016
    odoUpdateRateMax =  1

    rcChanUpdateRateMin = 0.016
    rcChanUpdateRateMax = 0.09

    vsimUpdateRateMin = 0.016
    vsimUpdateRateMax = 0.06

    SimMode = False #True = Simulated Mode, False = Real Mode
    
    routeState  = routeControl.RouteState(120.0)        #RouteState(near)
    firstWaypoint, secondWaypoint = routeState.waypoints[0], routeState.waypoints[1]
    odoState    = odoControl.OdoState(150, 150, firstWaypoint.angleTo_Degrees(routeState.waypoints[1]))    #OdoState(wheelDiaRt, wheelDiaLt,initTheta)
    rcChanState = rcChanControl.RcChanState(40, 40, 0.6, 0)    #RcChanState(lrChange, fwdbkChange, speedScaling, turnBias)
    trackState  = trackControl.TrackState(200,237,500, firstWaypoint.x, firstWaypoint.y)      #TrackState(wheelBase,trackWidth,movementBudget)
    vsimState   = vsimControl.VsimState(1.5,0.95,900.0) #VsimState(fricEffectPerSec,lrBias(0.95=Sim, 1.0=Real),speedMax)
    envSimState = envSimControl.EnvSimState()
    sensorState = sensorControl.SensorState(30,5)
    visualState = visualControl.VisualState()
    statsState = statsControl.StatsState()
    scanSimState  = scanSimControl.ScanSimState('IR', (0, 170), 0, 90, 650, 10)     # scanSimState (sensorID, sensorPosOffset(X,Y), sensorHeadingOffset, scanAngle, scanRange, turnSpeed)
    scanSimState2 = scanSimControl.ScanSimState('US', (0,-170), 180, 45, 650, 10)     # scanSimState (sensorID, sensorPosOffset(X,Y), sensorHeadingOffset, scanAngle, scanRange, turnSpeed)

    '''
    Section 3
    Amber Block
    '''
    routeController  = plumbing.controlloop.ControlLoop( routeState,  routeControl.routeControlUpdate,   0.20 * timeScale,  0.20 * timeScale)
    trackController  = plumbing.controlloop.ControlLoop( trackState,  trackControl.trackControlUpdate,   trackUpdateRateMin * timeScale,  trackUpdateRateMax * timeScale)
    if SimMode:
        odoController    = plumbing.controlloop.ControlLoop( odoState,    odoControl.simUpdate,              odoUpdateRateMin * timeScale,  odoUpdateRateMax * timeScale)
        rcChanController = plumbing.controlloop.ControlLoop( rcChanState, rcChanControl.simMotor,            rcChanUpdateRateMin * timeScale,  rcChanUpdateRateMax * timeScale)
    else:
        odoController    = plumbing.controlloop.ControlLoop( odoState,    odoControl.realUpdate,              odoUpdateRateMin * timeScale,  odoUpdateRateMax * timeScale)
        rcChanController = plumbing.controlloop.ControlLoop( rcChanState, rcChanControl.realMotor,            rcChanUpdateRateMin * timeScale,  rcChanUpdateRateMax * timeScale)
    vsimController   = plumbing.controlloop.ControlLoop( vsimState,   vsimControl.vsimControlUpdate,     vsimUpdateRateMin * timeScale,  vsimUpdateRateMax * timeScale)
    envSimController = plumbing.controlloop.ControlLoop( envSimState, envSimControl.envSimControlUpdate, 0.06 * timeScale,  0.06 * timeScale)
    sensorController = plumbing.controlloop.ControlLoop( sensorState, sensorControl.sensorControlUpdate, 0.06 * timeScale,  0.06 * timeScale)
    visualController = plumbing.controlloop.ControlLoop( visualState, visualControl.visualControlUpdate, 0.06 * guiTimeScale,  0.16 * guiTimeScale)
    statsController  = plumbing.controlloop.ControlLoop( statsState,  statsControl.statsControlUpdate,   0.5 * timeScale,  0.5 * timeScale)
    scanSimController = plumbing.controlloop.ControlLoop( scanSimState, scanSimControl.scanSimControlUpdate, 0.09 * timeScale, 0.09 * timeScale)
    scanSimController2 = plumbing.controlloop.ControlLoop( scanSimState2, scanSimControl.scanSimControlUpdate, 0.09 * timeScale, 0.09 * timeScale)

    '''
    Section 4
    Green Block
    '''
    routeController.connectTo(trackController,  routeControl.routeToTrackTranslator)
    routeController.connectTo(visualController,  routeControl.routeToVisualTranslator)
    trackController.connectTo(rcChanController, trackControl.trackToRcChanTranslator)
    rcChanController.connectTo(vsimController, rcChanControl.rcChanToVsimTranslator)
    vsimController.connectTo(odoController, vsimControl.vsimToOdoTranslator)
    odoController.connectTo(trackController, odoControl.odoToTrackTranslator)
    trackController.connectTo(routeController, trackControl.trackToRouteTranslator)
    #envSimController.connectTo(sensorController, envSimControl.envSimToSensorTranslator)
    sensorController.connectTo(trackController, sensorControl.sensorToTrackTranslator)
    envSimController.connectTo(visualController, envSimControl.envToVisualTranslator)
    trackController.connectTo(visualController, trackControl.trackToVisualTranslator)
    visualController.connectTo(routeController, visualControl.visualToRouteTranslator)
    #routeController.connectTo(statsController, statsControl.toStatsTranslator)
    trackController.connectTo(statsController, statsControl.toStatsTranslator)

    statsController.connectTo(visualController, statsControl.statsToVisualTranslator)
    trackController.connectTo(scanSimController, trackControl.trackToScanSimTranslator)
    envSimController.connectTo(scanSimController, envSimControl.envToScanSimControl)
    scanSimController.connectTo(visualController, scanSimControl.scanSimToVisualTranslator)
    scanSimController.connectTo(sensorController, scanSimControl.scanSimToSensorTranslator)
    trackController.connectTo(scanSimController2, trackControl.trackToScanSimTranslator)
    envSimController.connectTo(scanSimController2, envSimControl.envToScanSimControl)
    scanSimController2.connectTo(visualController, scanSimControl.scanSimToVisualTranslator)
    scanSimController2.connectTo(sensorController, scanSimControl.scanSimToSensorTranslator)
    rcChanController.connectTo(visualController, rcChanControl.rcChanToVsimTranslator)
    odoController.connectTo(visualController, odoControl.odoToVisualTranslator)


    visualController.connectTo(trackController, visualControl.visualToStartStop)       # application manager to stop loops
    visualController.connectTo(odoController, visualControl.visualToStartStop)
    #visualController.connectTo(statsController, visualControl.visualToStartStop)
    #visualController.connectTo(rcChanController, visualControl.visualToStartStop)
    #visualController.connectTo(envSimController, visualControl.visualToStartStop)
    #visualController.connectTo(sensorController, visualControl.visualToStartStop)
    #visualController.connectTo(routeController, visualControl.visualToStartStop)
    #visualController.connectTo(scanSimController, visualControl.visualToStartStop)
    #visualController.connectTo(scanSimController2, visualControl.visualToStartStop)
    #visualController.connectTo(routeController, visualControl.visualToStartStop)

    visualController.connectTo(trackController, visualControl.visualToQuit)       # application manager to stop loops
    visualController.connectTo(odoController, visualControl.visualToQuit)
##    visualController.connectTo(statsController, visualControl.visualToQuit)
##    visualController.connectTo(rcChanController, visualControl.visualToQuit)
##    visualController.connectTo(envSimController, visualControl.visualToQuit)
##    visualController.connectTo(sensorController, visualControl.visualToQuit)
##    visualController.connectTo(routeController, visualControl.visualToQuit)
##    visualController.connectTo(scanSimController, visualControl.visualToQuit)
##    visualController.connectTo(scanSimController2, visualControl.visualToQuit)
##    visualController.connectTo(routeController, visualControl.visualToQuit)
    visualController.connectTo(visualController, visualControl.visualToQuit)

    '''
    Section 5
    Amber Block
    '''
    routeController.start()
    trackController.start()
    rcChanController.start()
    vsimController.start()
    odoController.start()
    envSimController.start()
    sensorController.start()
    statsController.start()
    scanSimController.start()
    scanSimController2.start()

    visualController.run()
    print 'Good Night'
##    pygame.quit()       # quit the screen
##    sys.exit()

if __name__ == '__main__':

   runControlLoops()
